## v0.13.0

Changes since `v0.12.0`.

  New Features

  - Add alpha execution-attempt tracking behind the `ExecutionAttemptsTracking` feature gate (#1283, @jianqiaol)
    - Add `status.executionAttempts`, a monotonic counter covering the initial execution, failure-policy restarts, and suspend/resume cycles
    - Propagate the current attempt through the `jobset.sigs.k8s.io/execution-attempt` annotation on child Jobs and Pod templates
    - Add the Execution Attempts Tracking KEP (#1292, @jianqiaol)
  - Populate JobSet headless Service ports from container ports and keep owned Services in sync, enabling service meshes to route traffic to JobSet Pods (#1300, @yindia)
  - Apply `ttlSecondsAfterFinished` cleanup to externally managed JobSets after their controller records a terminal condition (#1315, @yindia)
  - Graduate the `TLSOptions` feature gate to GA; TLS minimum-version and cipher-suite configuration is now permanently enabled (#1297, @kannon92)

  Bug Fixes

  - Avoid a nil-pointer panic when reconciling JobSets without `spec.network` (#1266, @immanuwell)
  - Validate child resource names derived from `metadata.generateName` during JobSet creation (#1267, @immanuwell)
  - Ignore terminal leader Pods in the admission webhook so retried follower Pods do not deadlock after a leader failure (#1276, @jianqiaol)
  - Delete followers with malformed or mismatched topology placement so exclusive-placement reconciliation can repair them (#1269, @immanuwell)
  - Reject negative `replicatedJobs[].replicas` values in the CRD and admission webhook (#1279, @immanuwell)
  - Avoid nil-pointer panics when `volumeClaimPolicies[].retentionPolicy.whenDeleted` is omitted in programmatically constructed JobSets (#1305, @Viswalahiri)

  Helm/Deployment

  - Stop declaring webhook certificate Secret `data` fields in the Helm chart, preventing Helm v4 server-side-apply ownership conflicts during upgrades (#1248, @gzb1128)
  - Bootstrap webhook certificates before starting the main manager and disable bootstrap-only metrics and health listeners, avoiding startup failures and port collisions (#1243, @kannon92)
  - Increase the controller liveness-probe initial delay to tolerate certificate bootstrap and avoid transient container restarts (#1278, @kannon92)

  Documentation

  - Add a TPU multi-slice training guide with Kueue and JAX workload examples (#1168, @0xlen)
  - Add Workload Aware Scheduling guides and examples for gang scheduling, preemption, and topology-aware scheduling (#1241, @kannon92)
  - Add Dynamic Resource Allocation integration guidance for Workload Aware Scheduling (#1277, @sairameshv)
  - Add the Gang JobSets and Workload Aware Scheduling integration KEP and update it to use Workload builder types (#1253, #1313, @kannon92)
  - Add a KEP for mutable resources on suspended Jobs (#1274, @kannon92)
  - Add a KEP for JobSet `activeDeadlineSeconds` (#1306, @yindia)
  - Correct installation documentation references (#1256, @immanuwell)
  - Remove the obsolete Go Report Card badge (#1270, @tenzen-y)

  Build/CI Improvements

  - Add dedicated E2E coverage and configuration for alpha features, including in-place restart and per-Job restart (#1200, @IrvingMg)
  - Add a dedicated Kind environment and E2E suite for Workload Aware Scheduling (#1252, @kannon92)
  - Build Kind node images locally instead of relying on published node images (#1234, @kannon92)
  - Update Kind to 0.32.0 (#1260, @kannon92)
  - Probe the webhook request path before starting E2E tests to avoid connection-refused flakes (#1261, @kannon92)
  - Use standard feature-gate toggling to avoid Elastic JobSet test flakes (#1268, @kannon92)
  - Update the Cloud Build image (#1227, @kannon92)
  - Sync main with the v0.12.0 release artifacts (#1230, @kannon92)
  - Add CodeRabbit configuration (#1244, @kannon92)
  - Document the Kubernetes AI contribution policy for coding agents (#1240, @Copilot)

  Dependency Updates

  - Update Kubernetes dependencies from 0.36.0 to 0.37.0 and regenerate clients, CRDs, and the Python SDK (#1236, #1245, #1288, #1301, #1298, @kannon92)
  - Bump `sigs.k8s.io/controller-runtime` from 0.24.0 to 0.24.1 (#1236)
  - Bump `github.com/onsi/ginkgo/v2` from 2.28.3 to 2.32.1 (#1237, #1246, #1299)
  - Bump `github.com/onsi/gomega` from 1.40.0 to 1.43.0 (#1238, #1247, #1249, #1309)
  - Bump `sigs.k8s.io/structured-merge-diff/v6` from 6.4.0 to 6.4.2 (#1275)
  - Bump `google.golang.org/grpc` from 1.79.3 to 1.83.1 (#1285, #1312)
  - Bump `github.com/google/cel-go` from 0.26.0 to 0.29.2 (#1286, #1298)
  - Bump `github.com/prometheus/client_golang` from 1.23.2 to 1.24.1 (#1289)
  - Bump `github.com/go-logr/logr` from 1.4.3 to 1.4.4 (#1290)
  - Bump `github.com/stretchr/testify` from 1.11.1 to 1.12.1 (#1302)
  - Bump `golang.org/x/net` to 0.55.0 in the client-go example and Helm YAML processor modules (#1254, #1255)
  - Bump `postcss` from 8.5.13 to 8.5.23 in the documentation site (#1287)
  - Bump `browserslist` from 4.25.1 to 4.28.8 in the documentation site (#1311)
