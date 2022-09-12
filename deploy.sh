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
deploy_generic() {
    local environment="${1?No environment passed}"
    kubectl apply -k "deploy/$environment"
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
    local environment="${1?No environment passed}"
    if [[ ! -d "deploy/$environment" || "$environment" =~ ^(base|README)$ ]]; then
        echo "Unknown environment $environment, use one of:"
        ls deploy/ | egrep -v '^(base|README)'
        exit 1
    fi
    deploy_generic "$environment"
}
main "$@"