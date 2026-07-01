# KEP-969: Workload-Aware Scheduling Integration

<!-- toc -->
- [Summary](#summary)
- [Motivation](#motivation)
  - [Goals](#goals)
  - [Non-Goals](#non-goals)
- [Proposal](#proposal)
  - [User Stories](#user-stories)
    - [Story 1: Gang-Schedule an Entire Training JobSet](#story-1-gang-schedule-an-entire-training-jobset)
    - [Story 2: Topology-Constrained Workers with Independent Driver](#story-2-topology-constrained-workers-with-independent-driver)
    - [Story 3: Existing JobSets Work Without Changes](#story-3-existing-jobsets-work-without-changes)
    - [Story 4: Gang-Schedule a Single ReplicatedJob with Multiple Pods](#story-4-gang-schedule-a-single-replicatedjob-with-multiple-pods)
    - [Story 5: Suspended JobSets Do Not Create Scheduling Objects](#story-5-suspended-jobsets-do-not-create-scheduling-objects)
    - [Story 6: DependsOn with Gang Scheduling Uses Per-ReplicatedJob PodGroups](#story-6-dependson-with-gang-scheduling-uses-per-replicatedjob-podgroups)
    - [Story 7: ElasticJobSet Scaling Updates Scheduling Objects](#story-7-elasticjobset-scaling-updates-scheduling-objects)
    - [Story 8: Shared DRA ResourceClaim Across All Pods in a Job](#story-8-shared-dra-resourceclaim-across-all-pods-in-a-job)
  - [Risks and Mitigations](#risks-and-mitigations)
- [Design Details](#design-details)
  - [API](#api)
  - [Defaulting](#defaulting)
  - [Validation](#validation)
  - [Controller Integration](#controller-integration)
    - [Sequenced Startup (DependsOn / InOrder StartupPolicy)](#sequenced-startup-dependson--inorder-startuppolicy)
    - [ElasticJobSet Scaling](#elasticjobset-scaling)
      - [Known Upstream Blocker](#known-upstream-blocker)
  - [Workload Lifecycle](#workload-lifecycle)
  - [Test Plan](#test-plan)
    - [Unit Tests](#unit-tests)
    - [Integration Tests](#integration-tests)
  - [Graduation Criteria](#graduation-criteria)
    - [Alpha](#alpha)
    - [Beta](#beta)
- [Implementation History](#implementation-history)
- [Drawbacks](#drawbacks)
- [Alternatives](#alternatives)
  - [Option A: Template Delegation Model](#option-a-template-delegation-model)
<!-- /toc -->

## Summary

This KEP integrates [KEP-6089 Workload-Aware Scheduling (WAS) Controller APIs][kep-6089] into
JobSet. It adds an optional `spec.scheduling` field that lets users express gang scheduling,
topology constraints, and disruption policies for their JobSets. The feature is fully opt-in:
existing JobSets without the field are unaffected.

[kep-6089]: https://github.com/kubernetes/enhancements/tree/master/keps/sig-scheduling/6089-was-controller-apis

## Motivation

JobSet orchestrates groups of Jobs for distributed ML training and HPC workloads. These workloads
frequently need:

- **Gang scheduling:** All pods across all Jobs must be admitted together, or none at all.
- **Topology awareness:** Co-locate worker pods on the same rack or zone for network performance.
- **Coordinated disruption:** Preempting one pod should preempt the entire group.

Today, users cannot express these intents natively in a JobSet. KEP-6089 provides standardized
building blocks under `scheduling.k8s.io` and a `workloadbuilder` library. This KEP adopts those
building blocks to give JobSet users a first-class scheduling API.

### Goals

- Add an optional `spec.scheduling` field to `JobSetSpec` for expressing WAS intent.
- Support gang scheduling, topology constraints, and disruption modes at both the
  composite (whole JobSet) and leaf (per-ReplicatedJob) levels.
- Compile user intent into `Workload`/`CompositePodGroup`/`PodGroup` objects via the
  `workloadbuilder` library.
- Preserve 100% backward compatibility: JobSets without `spec.scheduling` behave identically
  to today.

### Non-Goals

- Modifying child Job templates to inject scheduling fields (we use the centralized model).
- Implementing the scheduler-side WAS features (Gang, TAS, WAP) — those are upstream.
- Supporting delegated `PodGroup` lifecycle management in the alpha phase.

## Proposal

Add a new optional `spec.scheduling` field to `JobSetSpec` behind a `WorkloadAwareScheduling`
feature gate. The field uses the centralized "Targeted Policies" model (Option B from KEP-6089),
where all scheduling configuration lives at the root level and targets ReplicatedJobs by name.
This aligns with JobSet's existing `targetReplicatedJobs` pattern used in `FailurePolicy` and
`SuccessPolicy`.

When `spec.scheduling` is set, the JobSet controller compiles a `Workload` resource (with a
`CompositePodGroup` root and one `PodGroup` per ReplicatedJob) and manages its lifecycle. When
`spec.scheduling` is omitted, no scheduling objects are created.

### User Stories

#### Story 1: Gang-Schedule an Entire Training JobSet

As an ML engineer, I want all 64 worker pods and 1 driver pod to be admitted atomically so that
my training job doesn't partially start and waste resources waiting for the rest.

```yaml
apiVersion: jobset.x-k8s.io/v1alpha2
kind: JobSet
metadata:
  name: pytorch-training
spec:
  scheduling:
    policy:
      gang: {}
  replicatedJobs:
    - name: driver
      replicas: 1
      template:
        spec:
          parallelism: 1
          completions: 1
          template:
            spec:
              containers:
                - name: driver
                  image: training:v1
    - name: workers
      replicas: 8
      template:
        spec:
          parallelism: 8
          completions: 8
          template:
            spec:
              containers:
                - name: worker
                  image: training:v1
```

**Result:** The JobSet controller creates a `Workload` with a composite Gang policy. All 65 pods
(1 driver + 64 workers) must be admitted together or none are scheduled.

#### Story 2: Topology-Constrained Workers with Independent Driver

As a platform engineer, I want worker pods co-located on the same network rack for RDMA
performance, but the driver can schedule anywhere independently.

```yaml
apiVersion: jobset.x-k8s.io/v1alpha2
kind: JobSet
metadata:
  name: rdma-training
spec:
  scheduling:
    policy:
      gang: {}
    replicatedJobPolicies:
      - targetReplicatedJob: "driver"
        policy:
          basic: {}
      - targetReplicatedJob: "workers"
        constraints:
          topology:
            - level: "topology.kubernetes.io/rack"
        disruption:
          all: {}
  replicatedJobs:
    - name: driver
      replicas: 1
      template:
        spec:
          parallelism: 1
          completions: 1
...
    - name: workers
      replicas: 16
      template:
        spec:
          parallelism: 4
          completions: 4
...
```

**Result:** The driver schedules independently (Basic). Workers are gang-scheduled (inherited
default), constrained to the same rack, and disrupted atomically. The composite Gang policy
ensures the overall JobSet is still admitted as a unit.

#### Story 3: Existing JobSets Work Without Changes

As a user with hundreds of existing JobSet manifests, I want zero behavior change when I upgrade
to a version that includes this feature.

```yaml
apiVersion: jobset.x-k8s.io/v1alpha2
kind: JobSet
metadata:
  name: existing-job
spec:
  # No scheduling field
  replicatedJobs:
    - name: workers
      replicas: 4
      template:
        spec:
          parallelism: 2
          completions: 2
          template:
            spec:
              containers:
                - name: worker
                  image: worker:v1
```

**Result:** No `Workload`, `PodGroup`, or `CompositePodGroup` objects are created. Standard
pod-by-pod Kubernetes scheduling. Identical to current behavior.

#### Story 4: Gang-Schedule a Single ReplicatedJob with Multiple Pods

As a data scientist, I have a simple parallel workload with a single ReplicatedJob that runs
multiple pods. I want all pods to be gang-scheduled so that they start together and none are
left waiting for resources, which would waste cluster capacity.

```yaml
apiVersion: jobset.x-k8s.io/v1alpha2
kind: JobSet
metadata:
  name: parallel-batch
spec:
  scheduling:
    policy:
      gang: {}
  replicatedJobs:
    - name: workers
      replicas: 1
      template:
        spec:
          parallelism: 4
          completions: 4
          completionMode: Indexed
          template:
            spec:
              restartPolicy: Never
              containers:
                - name: worker
                  image: batch-processor:v1
```

**Result:** The JobSet controller creates a single `PodGroup` with `gang.minCount=4`. All 4
pods from the single Job must be admitted together or none are scheduled. This is the simplest
possible gang-scheduling configuration — one ReplicatedJob, one Job, multiple pods.

#### Story 5: Suspended JobSets Do Not Create Scheduling Objects

As a platform engineer, when I create a JobSet in a suspended state (or suspend a running one),
I do not want any `Workload` or `PodGroup` objects to exist so that the scheduler does not
reserve resources for an inactive workload. When the JobSet is resumed, the scheduling objects
should be created automatically.

```yaml
apiVersion: jobset.x-k8s.io/v1alpha2
kind: JobSet
metadata:
  name: suspended-training
spec:
  suspend: true
  scheduling:
    policy:
      gang: {}
  replicatedJobs:
    - name: workers
      replicas: 1
      template:
        spec:
          parallelism: 4
          completions: 4
          completionMode: Indexed
          template:
            spec:
              restartPolicy: Never
              containers:
                - name: worker
                  image: batch-processor:v1
```

**Result:** While `suspend: true`, no `Workload` or `PodGroup` objects are created. When the
user patches `suspend` to `false`, the controller creates the `Workload` and a `PodGroup` with
`gang.minCount=4`, and scheduling proceeds normally.

#### Story 6: DependsOn with Gang Scheduling Uses Per-ReplicatedJob PodGroups

As an ML engineer, I have a training JobSet where workers depend on the driver being ready
before they start. I also want gang scheduling so that each group's pods are admitted
atomically. However, a single top-level PodGroup requiring all pods would deadlock because
the workers aren't created until the driver is ready.

```yaml
apiVersion: jobset.x-k8s.io/v1alpha2
kind: JobSet
metadata:
  name: sequenced-training
spec:
  scheduling:
    policy:
      gang: {}
  replicatedJobs:
    - name: driver
      replicas: 1
      template:
        spec:
          parallelism: 1
          completions: 1
          completionMode: Indexed
          template:
            spec:
              restartPolicy: Never
              containers:
                - name: driver
                  image: training:v1
    - name: workers
      replicas: 4
      dependsOn:
        - name: driver
          status: Ready
      template:
        spec:
          parallelism: 2
          completions: 2
          completionMode: Indexed
          template:
            spec:
              restartPolicy: Never
              containers:
                - name: worker
                  image: training:v1
```

**Result:** Even though only a top-level `gang: {}` policy is specified, the controller detects
the `dependsOn` configuration and automatically creates **per-ReplicatedJob PodGroups** instead
of a single top-level one. The driver PodGroup has `gang.minCount=1` and the workers PodGroup
has `gang.minCount=8`. This prevents deadlock while still ensuring each group is gang-scheduled.

The same behavior applies when using the deprecated `startupPolicy` with `InOrder`.

#### Story 7: ElasticJobSet Scaling Updates Scheduling Objects

As a platform engineer, I want to dynamically scale a running JobSet's parallelism (using the
ElasticJobSet feature) and have the scheduling objects automatically update to reflect the new
pod count.

```yaml
apiVersion: jobset.x-k8s.io/v1alpha2
kind: JobSet
metadata:
  name: elastic-training
spec:
  scheduling:
    policy:
      gang: {}
  replicatedJobs:
    - name: workers
      replicas: 1
      template:
        spec:
          parallelism: 4  # later scaled to 8
          completions: 4  # later scaled to 8
          completionMode: Indexed
          template:
            spec:
              restartPolicy: Never
              containers:
                - name: worker
                  image: training:v1
```

**Result:** Initially, a PodGroup with `gang.minCount=4` is created. When the user patches
`parallelism` and `completions` to 8, the controller detects the drift, deletes the stale
`Workload` and `PodGroup` (since their specs are immutable), and recreates them with
`gang.minCount=8`.


#### Story 8: Shared DRA ResourceClaim Across All Pods in a Job

As an ML engineer running multi-node GPU training, I need a single DRA ResourceClaim
(e.g., an IMEX channel or a multi-node TPU slice) that is shared across all pods in a
Job. Today, pod-level ResourceClaimTemplates create one ResourceClaim per pod, but
certain hardware resources — like NVLink IMEX channels or multi-node TPU slices — are
inherently shared across a group of pods and must be represented by a single
ResourceClaim that all pods reference.

See: https://github.com/kubernetes-sigs/jobset/issues/762

```yaml
apiVersion: jobset.x-k8s.io/v1alpha2
kind: JobSet
metadata:
  name: imex-training
spec:
  scheduling:
    policy:
      gang: {}
    replicatedJobPolicies:
      - targetReplicatedJob: "workers"
        constraints:
          topology:
            - level: "topology.kubernetes.io/rack"
        resourceClaims:
          - name: imex-channel
            resourceClaimTemplateName: imex-channel-template
  replicatedJobs:
    - name: workers
      replicas: 4
      template:
        spec:
          parallelism: 2
          completions: 2
          completionMode: Indexed
          ...
                  resources:
                    claims:
                      - name: gpu
                      - name: imex-channel
              resourceClaims:
                - name: gpu
                  resourceClaimTemplateName: gpu-template
                - name: imex-channel
                  resourceClaimName: <generated-by-podgroup>
```

In this example each worker pod still gets its own per-pod GPU ResourceClaim via the
pod-level `resourceClaims` field (`gpu-template`). Additionally, each PodGroup (one per
Job replica) gets a **single shared** ResourceClaim created from `imex-channel-template`.
Each pod must also include a pod-level `PodResourceClaim` entry (`resourceClaimName`)
and a corresponding `resources.claims` reference so that the shared IMEX claim is
actually bound to the pod. The `resourceClaimName` value is set by the controller to
the name of the ResourceClaim generated from the PodGroup-level template.
This enables multi-node GPU communication over NVLink.

**Result:** The JobSet controller creates one PodGroup per worker Job replica. Each
PodGroup carries a `resourceClaims` entry with `resourceClaimTemplateName:
imex-channel-template`. The WAS controller creates one ResourceClaim per PodGroup from
the template. Each pod in the PodGroup references the shared claim via its own
`PodResourceClaim` entry (injected by the JobSet mutating webhook), ensuring proper
binding. Pod-level GPU claims continue to work independently via their own
`resourceClaimTemplateName`. This resolves the need for Job-level
ResourceClaimTemplates without requiring changes to the core Job API.

### Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Upstream `scheduling.k8s.io/v1alpha3` types are not yet stable | Feature is gated as Alpha; types are behind `+featureGate` marker and can be swapped on graduation |
| Split-brain if upstream Job gains `spec.scheduling` | Webhook rejects JobSets that set both `spec.scheduling.replicatedJobPolicies` and embedded Job template scheduling fields |
| `workloadbuilder` library API churn | Pin vendored version; library is designed for backward-compatible evolution |
| `workloadbuilder` library is not yet merged upstream | The WAS controller APIs KEP (KEP-6089) and its `workloadbuilder` library are still under development. The JobSet controller will initially implement the Workload/PodGroup construction logic directly. Once `workloadbuilder` is merged and available as a consumable Go library, the controller will migrate to use it for building and validating scheduling objects. This is a code-quality improvement and does not affect the user-facing API. |
| ElasticJobSet scaling blocked when `GenericWorkload` is enabled ([kubernetes#140112](https://github.com/kubernetes/kubernetes/issues/140112)) | Unit-test the recreate path with mocked objects; defer integration/E2E tests until the upstream fix lands. ElasticJobSet + WAS is alpha-only and not expected in production before the fix. |

## Design Details

### API

New types added to `api/jobset/v1alpha2/jobset_types.go`:

```go
// JobSetScheduling defines Workload-Aware Scheduling configuration for a JobSet.
type JobSetScheduling struct {
    // policy defines the composite-level scheduling policy for the entire JobSet.
    // Defaults to Gang when spec.scheduling is set but policy is nil.
    // +optional
    Policy *schedulingv1alpha3.WorkloadCompositePodGroupSchedulingPolicy `json:"policy,omitempty"`

    // constraints defines composite-level topology constraints.
    // +optional
    Constraints *schedulingv1alpha3.WorkloadCompositePodGroupSchedulingConstraints `json:"constraints,omitempty"`

    // disruption defines how the entire composite group can be disrupted.
    // +optional
    Disruption *schedulingv1alpha3.WorkloadCompositePodGroupDisruptionMode `json:"disruption,omitempty"`

    // replicatedJobPolicies specifies per-ReplicatedJob leaf-level scheduling overrides.
    // +optional
    // +listType=map
    // +listMapKey=targetReplicatedJob
    ReplicatedJobPolicies []ReplicatedJobSchedulingPolicy `json:"replicatedJobPolicies,omitempty"`
}

// ReplicatedJobSchedulingPolicy targets a named ReplicatedJob with leaf-level scheduling config.
type ReplicatedJobSchedulingPolicy struct {
    // targetReplicatedJob is the name of the ReplicatedJob this policy applies to.
    TargetReplicatedJob string `json:"targetReplicatedJob"`

    // policy defines leaf-level scheduling policy (basic or gang).
    // Defaults to Gang when not specified.
    // +optional
    Policy *schedulingv1alpha3.WorkloadPodGroupSchedulingPolicy `json:"policy,omitempty"`

    // constraints defines leaf-level topology constraints.
    // +optional
    Constraints *schedulingv1alpha3.WorkloadPodGroupSchedulingConstraints `json:"constraints,omitempty"`

    // disruption defines how pods within this ReplicatedJob can be disrupted.
    // +optional
    Disruption *schedulingv1alpha3.WorkloadPodGroupDisruptionMode `json:"disruption,omitempty"`

    // resourceClaims specifies dynamic resource claims for this ReplicatedJob.
    // +optional
    ResourceClaims []schedulingv1alpha3.WorkloadPodGroupResourceClaim `json:"resourceClaims,omitempty"`
}
```

Add to `JobSetSpec`:

```go
type JobSetSpec struct {
    // ... existing fields ...

    // scheduling defines Workload-Aware Scheduling configuration.
    // When nil, no scheduling objects are created and behavior is unchanged.
    // When set (even to {}), the controller compiles a Workload resource.
    // +optional
    // +featureGate=WorkloadAwareScheduling
    Scheduling *JobSetScheduling `json:"scheduling,omitempty"`
}
```

### Defaulting

Defaulting only applies when `spec.scheduling != nil` (the field is present). The mutating
webhook never injects a `scheduling` block where one does not exist.

| Field | Default |
|---|---|
| `spec.scheduling.policy` | `{gang: {}}` |
| Each leaf `policy` (when not overridden via `replicatedJobPolicies`) | `{gang: {}}` |
| Leaf `gang.minCount` | `parallelism × replicas` for the ReplicatedJob |

### Validation

The validating webhook enforces:

1. Every `replicatedJobPolicies[*].targetReplicatedJob` must reference a valid
   `spec.replicatedJobs[*].name`.
2. No duplicate targets in `replicatedJobPolicies`.
3. Allow-list validation via `workloadbuilder` helpers (only `Basic`/`Gang` policies and
   `Single`/`All` disruption modes accepted).
4. `spec.scheduling` is immutable after creation.
5. If the feature gate is disabled, `spec.scheduling` is rejected.

### Controller Integration

When `WorkloadAwareScheduling` is enabled and `js.Spec.Scheduling != nil`, the reconciler:

1. Builds a `workloadbuilder.WorkloadItem` tree:
   - **Root node** (composite): maps `spec.scheduling.{policy,constraints,disruption}`.
   - **Leaf nodes** (one per ReplicatedJob): maps the matching `replicatedJobPolicies` entry,
     or uses the Gang default. A callback defaults `gang.minCount` to `parallelism × replicas`.

2. Calls `workloadbuilder.NewBuilder(root).Build(...)` to compile the `Workload` resource.

3. Creates/updates the `Workload` (owned by the JobSet via `OwnerReference`).

4. Annotates each child Job with:
   - `scheduling.k8s.io/group-template-name` → ReplicatedJob name
   - `scheduling.k8s.io/parent-composite-podgroup` → parent CompositePodGroup name

When `spec.scheduling` is nil, the reconciler skips all scheduling logic entirely.

#### Sequenced Startup (DependsOn / InOrder StartupPolicy)

When a JobSet uses `dependsOn` or an `InOrder` `startupPolicy`, Jobs are created sequentially.
A single top-level PodGroup requiring all pods (`minCount = total pods`) would deadlock because
not all pods exist simultaneously. To avoid this, the controller detects sequenced startup and
automatically falls back to **per-ReplicatedJob PodGroups**, even when only a top-level Gang
policy is specified. Each ReplicatedJob gets its own PodGroup with
`minCount = parallelism × replicas`, so each group is gang-scheduled independently.

`AnyOrder` `startupPolicy` does not trigger this behavior since all Jobs are created together.

#### ElasticJobSet Scaling

When the `ElasticJobSet` feature gate is enabled and `parallelism`/`completions` are scaled at
runtime, the computed `minCount` in PodGroups changes. Since `Workload` and `PodGroup` specs
are immutable, the controller detects the drift (`workloadNeedsRecreation`) and deletes both
the `Workload` and its `PodGroup`s, then recreates them with the updated `minCount` on the next
reconciliation.

The recreate flow is:

1. The controller computes the desired `minCount` from the current `parallelism × replicas`.
2. It compares the desired value against the existing `PodGroup` spec.
3. If they differ, the controller deletes the existing `Workload` and all child `PodGroup`s.
4. On the next reconciliation, the controller creates a new `Workload` and `PodGroup`s with
   the updated `minCount`.

This delete-and-recreate strategy is necessary because `Workload` and `PodGroup` specs are
immutable by design in the WAS API. In-place updates are not supported.

##### Known Upstream Blocker

ElasticJobSet scaling with WAS integration is currently blocked by an upstream Kubernetes
issue: [kubernetes/kubernetes#140112](https://github.com/kubernetes/kubernetes/issues/140112).
When the `GenericWorkload` feature gate is enabled in the cluster (which is required for WAS),
resizing any Job's `parallelism` or `completions` is forbidden by the Job API validation.
This means ElasticJobSet cannot scale Jobs at runtime when WAS is active, preventing
end-to-end testing of the PodGroup/Workload recreate path.

Until this upstream issue is resolved:

- The ElasticJobSet + WAS recreate logic will be implemented and covered by unit tests
  (mocking the Job resize), but **integration and E2E tests for this path are blocked**.
- The `workloadNeedsRecreation` detection code will be exercised in unit tests using
  pre-built objects with mismatched `minCount` values.
- Once the upstream fix lands, integration tests will be added to verify the full
  scale → delete → recreate lifecycle end-to-end.

### Workload Lifecycle

| JobSet Event | Action |
|---|---|
| Created with `scheduling` set | Create `Workload` + `CompositePodGroup` + child `PodGroup`s |
| Suspended | Delete `Workload` + `PodGroup`s so the scheduler releases resource claims |
| Resumed | Recreate `Workload` + `PodGroup`s (normal reconciliation path) |
| ElasticJobSet scaling | Delete and recreate `Workload` + `PodGroup`s with updated `minCount` |
| DependsOn / InOrder used | Force per-RJ `PodGroup`s instead of single top-level gang |
| Restarted | Recreate `PodGroup`s for the new attempt |
| Deleted | Automatic cleanup via OwnerReferences |
| Created without `scheduling` | No-op — no scheduling objects |

The alpha phase uses **centralized management**: the JobSet controller owns all scheduling
objects. Child Job controllers see the JobSet OwnerReference and skip their own Workload creation.

### Test Plan

#### Unit Tests

- `pkg/controllers/scheduling_test.go`:
  - `buildWorkloadTree` produces correct IR tree for various specs.
  - Gang defaults applied at root and leaf levels.
  - `minCount` callback computes `parallelism × replicas`.
  - User overrides (Basic escape hatch, topology, disruption) map correctly.
  - Nil `spec.scheduling` produces no tree (no-op).
- `pkg/webhooks/jobset_webhook_test.go`:
  - Invalid `targetReplicatedJob` references rejected.
  - Duplicate targets rejected.
  - Immutability enforced on update.
  - Feature gate disabled: field rejected.

#### Integration Tests

- `test/integration/`:
  - JobSet with `scheduling` creates correct `Workload` + scheduling objects.
  - Child Jobs carry downward mapping annotations.
  - Deletion cascades to `Workload` cleanup.
  - JobSet without `scheduling` creates zero scheduling objects.
  - Suspend/resume and restart correctly manage scheduling object lifecycle.

### Graduation Criteria

#### Alpha

- Feature gate `WorkloadAwareScheduling` added (default: disabled).
- API types, defaulting, and validation implemented.
- Controller compiles `Workload` via `workloadbuilder`.
- Unit and integration tests passing.

#### Beta

- Feedback gathered from early adopters.
- E2E tests with a real WAS-enabled cluster (Gang + TAS verified end-to-end).
- Evaluate whether to adopt delegated `PodGroup` lifecycle management.
- Feature gate default flipped to enabled.

## Implementation History

- 2026-06-28: KEP created.
- 2026-07-01: Added ElasticJobSet upstream blocker (kubernetes#140112) and noted
  that the `workloadbuilder` library is not yet merged upstream.

## Drawbacks

- Adds a dependency on `scheduling.k8s.io/v1alpha3` types which are pre-stable upstream.
- Introduces new scheduling objects (`Workload`, `PodGroup`, `CompositePodGroup`) that the
  controller must manage, increasing reconciliation complexity.

## Alternatives

### Option A: Template Delegation Model

KEP-6089 describes an alternative where leaf-level scheduling is configured inside the embedded
`JobTemplateSpec` (i.e., `spec.replicatedJobs[*].template.spec.scheduling`). This was rejected
because:

1. It splits scheduling config between two locations (root and nested templates).
2. It requires upstream Job to ship `spec.scheduling` first, creating a dependency bottleneck.
3. It diverges from JobSet's established `targetReplicatedJobs` pattern.

Option B (Centralized Targeted Policies) keeps all scheduling config in one place, avoids
upstream dependencies, and reuses a pattern JobSet users already know.
