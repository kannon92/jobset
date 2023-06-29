export KUSTOMIZE=$PWD/bin/kustomize
export GINKGO=$PWD/bin/ginkgo
export KIND=$PWD/bin/kind

function cleanup {
    if [ $USE_EXISTING_CLUSTER == 'false' ] 
    then
        if [ ! -d "$ARTIFACTS" ]; then
            mkdir -p "$ARTIFACTS"
        fi
        kubectl logs -n kube-system kube-scheduler-kind-control-plane > $ARTIFACTS/kube-scheduler.log || true
        kubectl logs -n kube-system kube-controller-manager-kind-control-plane > $ARTIFACTS/kube-controller-manager.log || true
        kubectl logs -n kueue-system deployment/kueue-controller-manager > $ARTIFACTS/kueue-controller-manager.log || true
        kubectl describe pods -n kueue-system > $ARTIFACTS/kueue-system-pods.log || true
        $KIND delete cluster --name $KIND_CLUSTER_NAME || { echo "You need to run make kind-image-build before this script"; exit -1; }
    fi
    (cd config/components/manager && $KUSTOMIZE edit set image controller=gcr.io/k8s-staging-jobset/jobset:main)
}
function startup {
    if [ $USE_EXISTING_CLUSTER == 'false' ] 
    then 
        $KIND create cluster --name $KIND_CLUSTER_NAME --image $E2E_KIND_VERSION --wait 1m
        kubectl get nodes > $ARTIFACTS/kind-nodes.log || true
        kubectl describe pods -n kube-system > $ARTIFACTS/kube-system-pods.log || true
    fi
}
function kind_load {
    $KIND load docker-image $IMAGE_TAG --name $KIND_CLUSTER_NAME
}
function jobset_deploy {
    echo "cd config/components/manager && $KUSTOMIZE edit set image controller=$IMAGE_TAG"
    (cd config/components/manager && $KUSTOMIZE edit set image controller=$IMAGE_TAG)
    echo "kubectl apply --server-side -k test/e2e/config" 
    kubectl apply --server-side -k test/e2e/config
}
trap cleanup EXIT
startup
kind_load
jobset_deploy
$GINKGO --junit-report=junit.xml --output-dir=$ARTIFACTS -v ./test/e2e/...