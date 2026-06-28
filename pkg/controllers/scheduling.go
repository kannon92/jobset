/*
Copyright The Kubernetes Authors.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package controllers

import (
	"context"
	"fmt"

	"github.com/go-logr/logr"
	schedulingv1alpha3 "k8s.io/api/scheduling/v1alpha3"
	apierrors "k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/klog/v2"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"

	jobset "sigs.k8s.io/jobset/api/jobset/v1alpha2"
)

const (
	// SchedulingGroupTemplateNameKey is the annotation set on child Jobs to map them
	// to their corresponding PodGroupTemplate in the parent Workload.
	SchedulingGroupTemplateNameKey = "scheduling.k8s.io/group-template-name"

	// SchedulingParentCompositePodGroupKey is the annotation set on child Jobs to
	// link them to the parent CompositePodGroup instance.
	SchedulingParentCompositePodGroupKey = "scheduling.k8s.io/parent-composite-podgroup"
)

// useTopLevelGang returns true when the top-level scheduling policy is Gang
// (or defaults to Gang) and there are no per-ReplicatedJob policy overrides.
// In this mode a single PodGroup is created so that all pods across every
// ReplicatedJob are gang-scheduled together.
//
// Top-level gang is disabled when DependsOn or InOrder StartupPolicy is used,
// because those features create Jobs sequentially. A single PodGroup requiring
// all pods would deadlock since not all pods exist simultaneously.
func useTopLevelGang(scheduling *jobset.JobSetScheduling) bool {
	if scheduling == nil {
		return false
	}
	// Any per-RJ overrides means we fall back to one PodGroup per RJ.
	if len(scheduling.ReplicatedJobPolicies) > 0 {
		return false
	}
	// If no explicit policy is set, the default is Gang.
	if scheduling.Policy == nil {
		return true
	}
	// Explicit Gang policy at the top level.
	return scheduling.Policy.Gang != nil
}

// hasSequencedStartup returns true when the JobSet uses DependsOn or an InOrder
// StartupPolicy. These features create Jobs sequentially, meaning not all pods
// exist at the same time. This affects how scheduling objects are compiled.
func hasSequencedStartup(js *jobset.JobSet) bool {
	// Check for InOrder startup policy.
	if js.Spec.StartupPolicy != nil && js.Spec.StartupPolicy.StartupPolicyOrder == jobset.InOrder {
		return true
	}
	// Check for DependsOn on any ReplicatedJob.
	for i := range js.Spec.ReplicatedJobs {
		if len(js.Spec.ReplicatedJobs[i].DependsOn) > 0 {
			return true
		}
	}
	return false
}

// totalMinCount computes the aggregate minCount across all ReplicatedJobs.
// If the top-level Gang policy specifies an explicit minCount, that value is
// used directly; otherwise the sum of parallelism*replicas for every
// ReplicatedJob is returned.
func totalMinCount(js *jobset.JobSet) int32 {
	if js.Spec.Scheduling != nil && js.Spec.Scheduling.Policy != nil &&
		js.Spec.Scheduling.Policy.Gang != nil && js.Spec.Scheduling.Policy.Gang.MinCount > 0 {
		return js.Spec.Scheduling.Policy.Gang.MinCount
	}
	var total int32
	for i := range js.Spec.ReplicatedJobs {
		total += computeMinCount(&js.Spec.ReplicatedJobs[i])
	}
	return total
}

// buildWorkload compiles a JobSet's scheduling configuration into a Workload resource.
func buildWorkload(js *jobset.JobSet) *schedulingv1alpha3.Workload {
	scheduling := js.Spec.Scheduling
	sequencedStartup := hasSequencedStartup(js)

	var templates []schedulingv1alpha3.PodGroupTemplate

	// When DependsOn or InOrder StartupPolicy is used, force per-RJ PodGroups
	// even if top-level gang is requested, because a single PodGroup requiring
	// all pods would deadlock when Jobs are created sequentially.
	if useTopLevelGang(scheduling) && !sequencedStartup {
		// Single PodGroupTemplate covering all ReplicatedJobs.
		templates = append(templates, buildTopLevelGangTemplate(js))
	} else {
		// Build per-ReplicatedJob policy lookup.
		leafPolicies := make(map[string]*jobset.ReplicatedJobSchedulingPolicy)
		if scheduling != nil {
			for i := range scheduling.ReplicatedJobPolicies {
				p := &scheduling.ReplicatedJobPolicies[i]
				leafPolicies[p.TargetReplicatedJob] = p
			}
		}

		for i := range js.Spec.ReplicatedJobs {
			rjob := &js.Spec.ReplicatedJobs[i]
			template := buildPodGroupTemplate(rjob, leafPolicies[rjob.Name], scheduling, sequencedStartup)
			templates = append(templates, template)
		}
	}

	workload := &schedulingv1alpha3.Workload{
		ObjectMeta: metav1.ObjectMeta{
			Name:      js.Name,
			Namespace: js.Namespace,
		},
		Spec: schedulingv1alpha3.WorkloadSpec{
			ControllerRef: &schedulingv1alpha3.TypedLocalObjectReference{
				APIGroup: jobset.GroupVersion.Group,
				Kind:     "JobSet",
				Name:     js.Name,
			},
			PodGroupTemplates: templates,
		},
	}

	return workload
}

// buildTopLevelGangTemplate creates a single PodGroupTemplate that gang-schedules
// all pods across every ReplicatedJob together.
func buildTopLevelGangTemplate(js *jobset.JobSet) schedulingv1alpha3.PodGroupTemplate {
	scheduling := js.Spec.Scheduling
	template := schedulingv1alpha3.PodGroupTemplate{
		Name: js.Name,
		SchedulingPolicy: schedulingv1alpha3.PodGroupSchedulingPolicy{
			Gang: &schedulingv1alpha3.GangSchedulingPolicy{
				MinCount: totalMinCount(js),
			},
		},
	}

	// Apply global constraints and disruption.
	if scheduling != nil {
		if scheduling.Constraints != nil {
			template.SchedulingConstraints = scheduling.Constraints
		}
		if scheduling.Disruption != nil {
			template.DisruptionMode = scheduling.Disruption
		}
	}

	// Propagate priorityClassName from the first ReplicatedJob's pod template.
	// In top-level gang mode all RJs share a single PodGroup, so the priority
	// should be consistent. We use the first RJ as the canonical source.
	if len(js.Spec.ReplicatedJobs) > 0 {
		template.PriorityClassName = js.Spec.ReplicatedJobs[0].Template.Spec.Template.Spec.PriorityClassName
	}

	return template
}

// buildPodGroupTemplate constructs a PodGroupTemplate for a single ReplicatedJob.
// Leaf-level overrides take priority; global scheduling config is used as a fallback.
func buildPodGroupTemplate(rjob *jobset.ReplicatedJob, leafPolicy *jobset.ReplicatedJobSchedulingPolicy, globalScheduling *jobset.JobSetScheduling, ignoreGlobalGangMinCount bool) schedulingv1alpha3.PodGroupTemplate {
	template := schedulingv1alpha3.PodGroupTemplate{
		Name: rjob.Name,
	}

	// Resolve scheduling policy (leaf override > global > default).
	policy := resolveLeafPolicy(rjob, leafPolicy, globalScheduling, ignoreGlobalGangMinCount)
	template.SchedulingPolicy = policy

	// Resolve constraints (leaf override > global).
	if leafPolicy != nil && leafPolicy.Constraints != nil {
		template.SchedulingConstraints = leafPolicy.Constraints
	} else if globalScheduling != nil && globalScheduling.Constraints != nil {
		template.SchedulingConstraints = globalScheduling.Constraints
	}

	// Resolve disruption mode (leaf override > global).
	if leafPolicy != nil && leafPolicy.Disruption != nil {
		template.DisruptionMode = leafPolicy.Disruption
	} else if globalScheduling != nil && globalScheduling.Disruption != nil {
		template.DisruptionMode = globalScheduling.Disruption
	}

	// Resolve resource claims.
	if leafPolicy != nil && len(leafPolicy.ResourceClaims) > 0 {
		template.ResourceClaims = leafPolicy.ResourceClaims
	}

	// Propagate priorityClassName from the ReplicatedJob's pod template.
	template.PriorityClassName = rjob.Template.Spec.Template.Spec.PriorityClassName

	return template
}

// resolveLeafPolicy determines the scheduling policy for a ReplicatedJob.
// Priority: leaf-level override > global scheduling policy > default Gang.
func resolveLeafPolicy(rjob *jobset.ReplicatedJob, leafPolicy *jobset.ReplicatedJobSchedulingPolicy, globalScheduling *jobset.JobSetScheduling, ignoreGlobalGangMinCount bool) schedulingv1alpha3.PodGroupSchedulingPolicy {
	// Priority 1: Leaf-level policy override.
	if leafPolicy != nil && leafPolicy.Policy != nil {
		p := *leafPolicy.Policy
		// Deep-copy the Gang pointer so we don't mutate the shared policy
		// when defaulting minCount for different ReplicatedJobs.
		if p.Gang != nil {
			gangCopy := *p.Gang
			p.Gang = &gangCopy
			if gangCopy.MinCount == 0 {
				p.Gang.MinCount = computeMinCount(rjob)
			}
		}
		return p
	}

	// Priority 2: Global scheduling policy.
	if globalScheduling != nil && globalScheduling.Policy != nil {
		p := *globalScheduling.Policy
		// Deep-copy the Gang pointer so we don't mutate the shared global policy
		// when defaulting minCount for different ReplicatedJobs.
		if p.Gang != nil {
			gangCopy := *p.Gang
			p.Gang = &gangCopy
			if gangCopy.MinCount == 0 || ignoreGlobalGangMinCount {
				p.Gang.MinCount = computeMinCount(rjob)
			}
		}
		return p
	}

	// Priority 3: Default Gang scheduling with minCount = parallelism * replicas.
	return schedulingv1alpha3.PodGroupSchedulingPolicy{
		Gang: &schedulingv1alpha3.GangSchedulingPolicy{
			MinCount: computeMinCount(rjob),
		},
	}
}

// computeMinCount returns parallelism * replicas for a ReplicatedJob.
func computeMinCount(rjob *jobset.ReplicatedJob) int32 {
	parallelism := int32(1)
	if rjob.Template.Spec.Parallelism != nil {
		parallelism = *rjob.Template.Spec.Parallelism
	}
	return parallelism * rjob.Replicas
}

// reconcileWorkload ensures the Workload resource for a JobSet exists and is up to date.
// When ElasticJobSet scaling changes parallelism, the Workload spec (which is
// immutable) may become stale. In that case we delete and recreate it.
func (r *JobSetReconciler) reconcileWorkload(ctx context.Context, js *jobset.JobSet) error {
	log := ctrl.LoggerFrom(ctx)

	desired := buildWorkload(js)

	// Set JobSet as the owner of the Workload.
	if err := ctrl.SetControllerReference(js, desired, r.Scheme); err != nil {
		return fmt.Errorf("setting controller reference on Workload: %w", err)
	}

	// Try to get existing Workload.
	existing := &schedulingv1alpha3.Workload{}
	err := r.Get(ctx, client.ObjectKeyFromObject(desired), existing)
	if apierrors.IsNotFound(err) {
		log.V(2).Info("Creating Workload for JobSet", "workload", klog.KObj(desired))
		return r.Create(ctx, desired)
	}
	if err != nil {
		return fmt.Errorf("getting Workload: %w", err)
	}

	// If the Workload spec has drifted (e.g., ElasticJobSet scaling changed
	// parallelism), the immutable Workload must be deleted and recreated.
	if workloadNeedsRecreation(existing, desired) {
		log.V(2).Info("Workload spec drifted, recreating", "workload", klog.KObj(existing))
		if err := r.deleteSchedulingObjects(ctx, js); err != nil {
			return fmt.Errorf("deleting stale scheduling objects: %w", err)
		}
		log.V(2).Info("Creating updated Workload for JobSet", "workload", klog.KObj(desired))
		return r.Create(ctx, desired)
	}

	// Workload exists and matches desired state.
	return nil
}

// workloadNeedsRecreation returns true if the existing Workload's
// PodGroupTemplates differ from the desired state. This happens when
// ElasticJobSet scaling changes the parallelism of a ReplicatedJob,
// causing the computed minCount to change.
func workloadNeedsRecreation(existing, desired *schedulingv1alpha3.Workload) bool {
	if len(existing.Spec.PodGroupTemplates) != len(desired.Spec.PodGroupTemplates) {
		return true
	}
	for i := range existing.Spec.PodGroupTemplates {
		e := &existing.Spec.PodGroupTemplates[i]
		d := &desired.Spec.PodGroupTemplates[i]
		if e.Name != d.Name {
			return true
		}
		// Compare Gang minCount — the most common drift from elastic scaling.
		if e.SchedulingPolicy.Gang != nil && d.SchedulingPolicy.Gang != nil {
			if e.SchedulingPolicy.Gang.MinCount != d.SchedulingPolicy.Gang.MinCount {
				return true
			}
		}
		// Policy type changed (e.g., Gang → Basic or vice versa).
		if (e.SchedulingPolicy.Gang == nil) != (d.SchedulingPolicy.Gang == nil) {
			return true
		}
		if (e.SchedulingPolicy.Basic == nil) != (d.SchedulingPolicy.Basic == nil) {
			return true
		}
	}
	return false
}

// reconcilePodGroups ensures PodGroup resources exist for the JobSet.
// When the top-level gang policy applies, a single PodGroup is created for the
// entire JobSet. Otherwise one PodGroup is created per ReplicatedJob.
func (r *JobSetReconciler) reconcilePodGroups(ctx context.Context, js *jobset.JobSet) error {
	log := ctrl.LoggerFrom(ctx)

	scheduling := js.Spec.Scheduling

	if useTopLevelGang(scheduling) && !hasSequencedStartup(js) {
		return r.reconcileSinglePodGroup(ctx, js, log)
	}

	return r.reconcilePerReplicatedJobPodGroups(ctx, js, log)
}

// reconcileSinglePodGroup creates one PodGroup that gang-schedules all pods together.
func (r *JobSetReconciler) reconcileSinglePodGroup(ctx context.Context, js *jobset.JobSet, log logr.Logger) error {
	template := buildTopLevelGangTemplate(js)

	pgName := js.Name
	desired := &schedulingv1alpha3.PodGroup{
		ObjectMeta: metav1.ObjectMeta{
			Name:      pgName,
			Namespace: js.Namespace,
		},
		Spec: schedulingv1alpha3.PodGroupSpec{
			PodGroupTemplateRef: &schedulingv1alpha3.PodGroupTemplateReference{
				Workload: &schedulingv1alpha3.WorkloadPodGroupTemplateReference{
					WorkloadName:         js.Name,
					PodGroupTemplateName: js.Name,
				},
			},
			SchedulingPolicy:      template.SchedulingPolicy,
			SchedulingConstraints: template.SchedulingConstraints,
			DisruptionMode:        template.DisruptionMode,
			PriorityClassName:     template.PriorityClassName,
		},
	}

	if err := ctrl.SetControllerReference(js, desired, r.Scheme); err != nil {
		return fmt.Errorf("setting controller reference on PodGroup %s: %w", pgName, err)
	}

	existing := &schedulingv1alpha3.PodGroup{}
	err := r.Get(ctx, client.ObjectKeyFromObject(desired), existing)
	if apierrors.IsNotFound(err) {
		log.V(2).Info("Creating single PodGroup for JobSet", "podGroup", pgName)
		if err := r.Create(ctx, desired); err != nil {
			return fmt.Errorf("creating PodGroup %s: %w", pgName, err)
		}
		return nil
	}
	if err != nil {
		return fmt.Errorf("getting PodGroup %s: %w", pgName, err)
	}

	// PodGroup exists; spec is immutable so no update needed.
	return nil
}

// reconcilePerReplicatedJobPodGroups creates one PodGroup per ReplicatedJob.
func (r *JobSetReconciler) reconcilePerReplicatedJobPodGroups(ctx context.Context, js *jobset.JobSet, log logr.Logger) error {
	scheduling := js.Spec.Scheduling
	sequencedStartup := hasSequencedStartup(js)
	leafPolicies := make(map[string]*jobset.ReplicatedJobSchedulingPolicy)
	if scheduling != nil {
		for i := range scheduling.ReplicatedJobPolicies {
			p := &scheduling.ReplicatedJobPolicies[i]
			leafPolicies[p.TargetReplicatedJob] = p
		}
	}

	for i := range js.Spec.ReplicatedJobs {
		rjob := &js.Spec.ReplicatedJobs[i]
		template := buildPodGroupTemplate(rjob, leafPolicies[rjob.Name], scheduling, sequencedStartup)

		pgName := podGroupName(js.Name, rjob.Name)
		desired := &schedulingv1alpha3.PodGroup{
			ObjectMeta: metav1.ObjectMeta{
				Name:      pgName,
				Namespace: js.Namespace,
			},
			Spec: schedulingv1alpha3.PodGroupSpec{
				PodGroupTemplateRef: &schedulingv1alpha3.PodGroupTemplateReference{
					Workload: &schedulingv1alpha3.WorkloadPodGroupTemplateReference{
						WorkloadName:         js.Name,
						PodGroupTemplateName: rjob.Name,
					},
				},
				SchedulingPolicy:      template.SchedulingPolicy,
				SchedulingConstraints: template.SchedulingConstraints,
				DisruptionMode:        template.DisruptionMode,
				ResourceClaims:        template.ResourceClaims,
				PriorityClassName:     template.PriorityClassName,
			},
		}

		if err := ctrl.SetControllerReference(js, desired, r.Scheme); err != nil {
			return fmt.Errorf("setting controller reference on PodGroup %s: %w", pgName, err)
		}

		existing := &schedulingv1alpha3.PodGroup{}
		err := r.Get(ctx, client.ObjectKeyFromObject(desired), existing)
		if apierrors.IsNotFound(err) {
			log.V(2).Info("Creating PodGroup for ReplicatedJob", "podGroup", pgName, "replicatedJob", rjob.Name)
			if err := r.Create(ctx, desired); err != nil {
				return fmt.Errorf("creating PodGroup %s: %w", pgName, err)
			}
			continue
		}
		if err != nil {
			return fmt.Errorf("getting PodGroup %s: %w", pgName, err)
		}

		// PodGroup exists; spec is immutable so no update needed.
	}

	return nil
}

// deleteSchedulingObjects removes the Workload and all PodGroups owned by the
// JobSet. This is called when a JobSet is suspended so that the scheduler
// releases all resource claims. The objects are recreated when the JobSet is
// resumed.
func (r *JobSetReconciler) deleteSchedulingObjects(ctx context.Context, js *jobset.JobSet) error {
	log := ctrl.LoggerFrom(ctx)

	// Delete PodGroups owned by this JobSet.
	var pgList schedulingv1alpha3.PodGroupList
	if err := r.List(ctx, &pgList, client.InNamespace(js.Namespace)); err != nil {
		return fmt.Errorf("listing PodGroups: %w", err)
	}
	for i := range pgList.Items {
		pg := &pgList.Items[i]
		if !metav1.IsControlledBy(pg, js) {
			continue
		}
		log.V(2).Info("Deleting PodGroup for suspended JobSet", "podGroup", klog.KObj(pg))
		if err := r.Delete(ctx, pg); client.IgnoreNotFound(err) != nil {
			return fmt.Errorf("deleting PodGroup %s: %w", pg.Name, err)
		}
	}

	// Delete the Workload.
	workload := &schedulingv1alpha3.Workload{}
	workload.Name = js.Name
	workload.Namespace = js.Namespace
	log.V(2).Info("Deleting Workload for suspended JobSet", "workload", klog.KObj(workload))
	if err := r.Delete(ctx, workload); client.IgnoreNotFound(err) != nil {
		return fmt.Errorf("deleting Workload %s: %w", workload.Name, err)
	}

	return nil
}

// podGroupName generates a deterministic PodGroup name from the JobSet and ReplicatedJob names.
func podGroupName(jobSetName, replicatedJobName string) string {
	return fmt.Sprintf("%s-%s", jobSetName, replicatedJobName)
}
