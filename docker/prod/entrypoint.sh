#!/bin/sh -e

check_passed=0

run_check() {
    if [ "${check_passed}" -ne 0 ]; then
        return
    fi
    python manage.py check --deploy
    # django-admin check --deploy
    check_passed=1
}

main() {
    BASENAME="$(basename "$0")"
    if [ "$#" -lt 1 ]; then
        echo "Usage: ${BASENAME} COMMAND..."
        echo
        echo "Available commands are:"
        echo
        echo "  migrate        Runs Django migrations"
        echo "  run-server     Starts Gunicorn server"
        echo "  collectstatic  Collects static files"
        echo "  nginx          Runs nginx to serve static files"
        echo
        exit
    fi
    for command in "$@"; do
        case "${command}" in
            "migrate")
                run_check

                python manage.py migrate --no-input
                # django-admin migrate --no-input
                ;;
            "run-server")
                run_check

                exec gunicorn --bind "${GUNICORN_HOST}" --workers="${GUNICORN_WORKERS}" trojsten.wsgi:application
                ;;
            "collectstatic")
                run_check

                python manage.py collectstatic --no-input
                # django-admin collectstatic --no-input
                ;;
            "nginx")
                nginx -g "pid /tmp/nginx.pid; daemon off;"
                ;;
            *)
                echo "Unknown ${BASENAME} command '${command}'." >&2
                exit 1
                ;;
        esac
    done
}

main "$@"