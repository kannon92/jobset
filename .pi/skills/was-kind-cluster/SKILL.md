---
name: was-kind-cluster
description: Creates a Kind cluster with Workload-Aware Scheduling (WAS) feature gates enabled, deploys JobSet, and provides targets for running scheduling-specific E2E tests. Use when setting up a local dev/test environment for WAS integration.
---

# WAS Kind Cluster

Sets up a local Kind cluster with Kubernetes WAS feature gates enabled (on the apiserver and scheduler), deploys the JobSet controller, and provides E2E tests for verifying the setup. No JobSet-side feature gate is required — WAS support is always available when the cluster APIs are present.

## Prerequisites

- Docker running
- `go` installed (for building JobSet and the Kind node image from K8s source)
- No existing Kind cluster named `was-test` (or set `WAS_KIND_CLUSTER_NAME` to override)
- Sufficient disk space and memory for `kind build node-image` (downloads Kubernetes server binaries from CI)

## Quick Start

All operations are available as Makefile targets:

```bash
# Build image, create cluster, deploy JobSet with WAS enabled
make kind-cluster-scheduling

# Run scheduling E2E tests (creates cluster, deploys, runs tests, cleans up)
make test-e2e-kind-scheduling

# Tear down the cluster (collects logs first)
make kind-cluster-scheduling-delete
```

To use a custom cluster name:

```bash
make kind-cluster-scheduling WAS_KIND_CLUSTER_NAME=my-was-cluster
make kind-cluster-scheduling-delete WAS_KIND_CLUSTER_NAME=my-was-cluster
```

### Legacy wrapper scripts

The `scripts/` directory contains thin wrappers around the make targets for
backward compatibility:

```bash
./scripts/setup.sh       # → make kind-cluster-scheduling
./scripts/teardown.sh    # → make kind-cluster-scheduling-delete
```

## Step-by-Step

If you prefer to run steps individually:

### 1. Build the Kind node image from Kubernetes CI

The WAS (Workload-Aware Scheduling) APIs require Kubernetes built from main.
The setup uses `kind build node-image` to build a node image from the latest
K8s CI build to ensure the `scheduling.k8s.io` API group is available.

```bash
make kind-k8s-main-image-build
```

### 2. Build the JobSet image for Kind

```bash
make kind-image-build
```

### 3. Create the Kind cluster with WAS feature gates and deploy

```bash
make kind-cluster-scheduling
```

### 4. Run the scheduling E2E tests

```bash
make test-e2e-kind-scheduling
```

### 5. Verification checklist

After the cluster is up, confirm:

| Check | Command |
|-------|---------|
| WAS API types are registered | `kubectl api-resources \| grep scheduling.k8s.io` |
| JobSet controller is running | `kubectl get pods -n jobset-system` |


### 6. Tear down

```bash
make kind-cluster-scheduling-delete
```

## Architecture

The WAS cluster lifecycle is implemented in shared scripts under `hack/`:

| File | Purpose |
|------|---------|
| `hack/e2e-scheduling-cluster.sh` | Shared functions: create/delete cluster, deploy JobSet, verify APIs |
| `hack/e2e-scheduling-test.sh` | CI entrypoint: create → deploy → Ginkgo tests → cleanup |
| `hack/kind-config-scheduling.yaml` | Kind cluster config with WAS feature gates |

| `test/e2e/scheduling/` | Ginkgo E2E test suite |

Makefile targets:

| Target | Description |
|--------|-------------|
| `kind-k8s-main-image-build` | Build Kind node image from K8s CI main |
| `kind-cluster-scheduling` | Build images, create cluster, deploy controller |
| `kind-cluster-scheduling-delete` | Collect logs and delete cluster |
| `test-e2e-kind-scheduling` | Full CI: create → deploy → Ginkgo e2e → cleanup |

## Troubleshooting

```bash
# Check controller logs for scheduling reconciliation
kubectl logs -n jobset-system deployment/jobset-controller-manager | grep -i scheduling

# Check WAS API types are registered
kubectl api-resources | grep scheduling.k8s.io

# Check node image version
docker images | grep jobset/kind-node
```
