#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail


help() {
    cat <<EOH
    Usage: $0 [OPTIONS] <ENVIRONMENT>
    Options:
      -h        Show this help.
      -v        Show verbose output.
EOH
}


check_environment() {
    # verify that the proper environment is passed
    local environment="${1?No environment passed}"

    if [[ ! -d "deploy/$environment" || "$environment" =~ ^(base|README)$ ]]; then
        echo "Unknown environment $environment, use one of:"
        ls deploy/ | egrep -v '^(base|README)'
        exit 1
    fi
}


deploy_generic() {
    local environment="${1?No environment passed}"

    if [[ "$environment" == "devel" ]]; then
        sed "s/{{HARBOR_IP}}/${HARBOR_IP}/"\
          deploy/devel/auth-patch.yaml.template > deploy/devel/auth-patch.yaml
    fi

    if command -v minikube >/dev/null; then
         kubectl="minikube kubectl --"
    else
        kubectl="kubectl"
    fi
    
    $kubectl apply -k "deploy/base-tekton"
    $kubectl apply -k "deploy/$environment"
}


main () {
    while getopts "hv" option; do
        case "${option}" in
        h)
            help
            exit 0
            ;;
        v) set -x;;
        *)
            echo "Wrong option $option"
            help
            exit 1
            ;;
        esac
    done
    shift $((OPTIND-1))
    
    # default to prod, avoid deploying dev in prod if there's any issue
    local environment="tools"
    if [[ "${1:-}" == "" ]]; then
        if [[ -f /etc/wmcs-project ]]; then
            environment="$(cat /etc/wmcs-project)"
        fi
    else
        environment="${1:-}"
    fi

    check_environment "$environment"
    deploy_generic "$environment"
}


main "$@"
