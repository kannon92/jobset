#!/usr/bin/env bash
# Setup vendor directory with scheduling/v1alpha3 types from k8s main.
#
# The scheduling.k8s.io/v1alpha3 API is not yet released in a tagged version
# of k8s.io/api. This script vendors all Go dependencies and then copies the
# v1alpha3 scheduling types from a local checkout or downloads them from k8s
# main, following the same pattern used by Kueue.
#
# Usage:
#   ./hack/setup-vendor.sh
#   K8S_API_SOURCE=../path/to/k8s.io/api ./hack/setup-vendor.sh

set -o errexit
set -o nounset
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENDOR_SCHEDULING="${REPO_ROOT}/vendor/k8s.io/api/scheduling"

cd "$REPO_ROOT"

echo "==> Running go mod vendor..."
go mod vendor

if [ -d "${VENDOR_SCHEDULING}/v1alpha3" ]; then
    echo "==> scheduling/v1alpha3 already exists in vendor, skipping copy."
else
    echo "==> Adding scheduling/v1alpha3 types to vendor..."

    if [ -n "${K8S_API_SOURCE:-}" ] && [ -d "${K8S_API_SOURCE}/scheduling/v1alpha3" ]; then
        echo "    Copying from local source: ${K8S_API_SOURCE}/scheduling/v1alpha3"
        cp -r "${K8S_API_SOURCE}/scheduling/v1alpha3" "${VENDOR_SCHEDULING}/v1alpha3"
    else
        echo "    Downloading from k8s.io/api@v0.37.0-alpha.2..."
        TMPDIR="$(mktemp -d)"
        trap "rm -rf ${TMPDIR}" EXIT
        cd "$TMPDIR"
        go mod init tmp
        GOPATH="${TMPDIR}/gopath" go mod download k8s.io/api@v0.37.0-alpha.2
        V1ALPHA3_SRC=$(find "${TMPDIR}/gopath/pkg/mod/k8s.io" -path "*/scheduling/v1alpha3" -maxdepth 5 2>/dev/null | head -1)
        if [ -z "$V1ALPHA3_SRC" ]; then
            echo "ERROR: Could not find scheduling/v1alpha3 in downloaded module"
            exit 1
        fi
        cp -r "$V1ALPHA3_SRC" "${VENDOR_SCHEDULING}/v1alpha3"
        cd "$REPO_ROOT"
    fi

    # Add the package to vendor/modules.txt
    if ! grep -q "k8s.io/api/scheduling/v1alpha3" vendor/modules.txt; then
        sed -i '/k8s.io\/api\/scheduling\/v1alpha2/a k8s.io/api/scheduling/v1alpha3' vendor/modules.txt
    fi
fi

echo "==> Verifying vendor build..."
go build -mod=vendor ./...
echo "✅ Vendor setup complete with scheduling/v1alpha3 support."
