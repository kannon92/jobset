# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - Changes since v0.8.0

### New Features

- **feat: support multiple items in DependsOn API** (#878) - Added support for specifying multiple dependencies in the DependsOn field
- **feat: add example for multiple DependsOn items** (#895) - Added example demonstrating the new multiple DependsOn functionality
- **Add a JobSet label for Pods with the UID of the JobSet** (#862) - Enhanced pod labeling with JobSet UID for better tracking
- **Add group labels / annotations for replicated jobs grouping** (#822) - Added labeling support for grouping replicated jobs
- **Add example for replicated job groups** (#839) - Added example demonstrating replicated job grouping
- **feat(docs): Create JobSet adopters page** (#852) - Added adopters page to documentation
- **Enable TLS metrics** (#863) - Added TLS support for metrics endpoint

### Bug Fixes

- **remove omitempty annotation for restarts fields** (#905) - Fixed serialization issue with restart fields
- **fix: certificate fails to find issuer** (#868) - Fixed certificate issuer discovery issue
- **bug fix: fix depends on validation if there are no replicated jobs** (#819) - Fixed validation when no replicated jobs are present
- **fix wrong cmd of output service** (#815) - Corrected service output command
- **fix repository bug** (#803) - Fixed repository-related issue
- **fix(sdk): Add Kubernetes refs to the JobSet OpenAPI swagger** (#810) - Fixed SDK OpenAPI references

### Improvements

- **separate metrics one label [<name>/<namespace>] to two label [<name>, <namespace>]** (#889) - Improved metrics labeling structure
- **Simplify replicatedJob name validations** (#881) - Streamlined validation logic
- **chore: Replace completionModePtr with ptr.To()** (#883) - Code modernization using newer pointer utilities
- **Default to 8443 as metrics port to align service instead of 8080** (#844) - Changed default metrics port for better alignment
- **Set readOnlyRootFilesystem explicitly to true** (#845) - Enhanced security by enforcing read-only root filesystem
- **chore: Upgrade the default k8s versions for E2E and integration tests cluster** (#882) - Updated test cluster versions

### Documentation

- **docs: Use correct links to examples** (#901) - Fixed broken example links
- **docs: support multiple items in DependsOn API** (#877) - Added documentation for multiple DependsOn feature
- **docs: redirect / to /docs/overview** (#859) - Improved documentation navigation
- **Fix broken helm link to correct one** (#903) - Fixed Helm documentation links
- **fix link for depends on** (#896) - Fixed DependsOn documentation links
- **Fix typo in JobSetStatus.TeminalState docs** (#871) - Fixed documentation typo
- **mention field paths and values of invalid fields** (#869) - Enhanced error message documentation
- **Update the helm repo link** (#812) - Updated Helm repository links
- **add minimal helm installation instructions** (#811) - Added basic Helm installation guide
- **Update documentation with latest release** (#808) - Updated docs for latest release
- **update toc for kep 672** (#890) - Updated KEP documentation table of contents
- **update reference data** (#804) - Updated API reference documentation

### Helm & Deployment

- **update helm CRD to include ReplicatedJob groupName** (#870) - Enhanced Helm CRD with group name support
- **Add .helmignore file to ignore files when packging Helm chart** (#823) - Added Helm packaging configuration
- **add helm verify step and fix some minor items** (#851) - Improved Helm chart verification
- **move subcharts to nested level** (#842) - Reorganized Helm chart structure

### Dependencies & Build

- **Bump sigs.k8s.io/controller-runtime in the kubernetes group** (#911) - Updated controller-runtime dependency
- **Bump the kubernetes group with 6 updates** (#906) - Updated multiple Kubernetes dependencies
- **update kubernetes to 0.33** (#894) - Updated Kubernetes dependencies to v0.33
- **update k8s dependencies to 0.32.3 without dependabot** (#840) - Updated Kubernetes dependencies
- **Bump the kubernetes group with 2 updates** (#830) - Additional Kubernetes dependency updates
- **Bump sigs.k8s.io/structured-merge-diff/v4 in the kubernetes group** (#879) - Updated structured-merge-diff dependency
- **Bump sigs.k8s.io/controller-runtime in the kubernetes group** (#861) - Another controller-runtime update
- **update golang to 1.24** (#841) - Updated Go version to 1.24
- **bump builder golang image to 1.24** (#864) - Updated builder image to Go 1.24
- **Bump golang.org/x/net from 0.37.0 to 0.38.0** (#887) - Updated networking dependency
- **Bump golang.org/x/net in /site/static/examples/client-go** (#888, #886) - Updated client-go examples
- **Bump github.com/prometheus/client_golang from 1.21.1 to 1.22.0** (#880) - Updated Prometheus client
- **Bump github.com/prometheus/client_golang from 1.21.0 to 1.21.1** (#831) - Earlier Prometheus client update
- **Bump github.com/onsi/gomega from 1.36.3 to 1.37.0** (#867) - Updated Gomega testing framework
- **Bump github.com/onsi/gomega from 1.36.2 to 1.36.3** (#849) - Earlier Gomega update
- **Bump github.com/onsi/ginkgo/v2 from 2.23.3 to 2.23.4** (#866) - Updated Ginkgo testing framework
- **Bump github.com/onsi/ginkgo/v2 from 2.22.2 to 2.23.0** (#832) - Earlier Ginkgo update
- **Bump postcss from 8.4.21 to 8.5.3 in /site** (#885) - Updated PostCSS for site
- **Bump OpenAPI Generator CLI to v7.11.0** (#806) - Updated OpenAPI generator

### Development & Tooling

- **update kind to 0.29.0** (#913) - Updated Kind for local development
- **update golangci to v2** (#897) - Updated golangci-lint to v2
- **Update kustomize version to v5.2.1** (#892) - Updated Kustomize version
- **update controller tools to v0.17.2** (#833) - Updated controller-tools
- **bump envtest to 1.31** (#828) - Updated envtest framework
- **pin envtest** (#821) - Pinned envtest version for stability
- **add yq to artifacts makefile** (#850) - Added yq tool to build artifacts
- **update with latest release** (#856) - Updated release information

## [v0.8.0] - Previous Release

For changes in v0.8.0 and earlier releases, please refer to the [GitHub Releases](https://github.com/kubernetes-sigs/jobset/releases) page.