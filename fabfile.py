import os
from fabric.api import cd, env, get, lcd, local, prefix, run, sudo
from fabric.context_managers import shell_env

env.hosts = ["metal.raesener.de"]


def create_container():
    "create the sblog container locally and upload to docker repo"
    local("python manage.py compilescss")
    local("docker-compose build app")
    local("python manage.py compilescss --delete-files")


def push_container():
    local("docker push elmcrest/sblog")


def deploy_container():
    with cd("infrastructure"):
        with shell_env(POSTGRES_PASSWORD=os.environ.get("POSTGRES_PASSWORD")):
            run("docker-compose stop sblog")
            run("docker-compose pull sblog")
            run("docker-compose up -d sblog")


def create_and_deploy():
    create_container()
    push_container()
    deploy_container()


def fetchdb():
    "fetch remote database, see dockergetdb"
    container = "systori_db_sblog_1"
    dbname = "sblog"
    dump_file = "sblog.dump"
    docker_dump_folder = "/var/lib/postgresql/dumps"
    host_dump_folder = "/home/elmcrest/sblog/postgresql/dumps"
    docker_dump_path = os.path.join(docker_dump_folder, dump_file)
    host_dump_path = os.path.join(host_dump_folder, dump_file)
    # -Fc : custom postgresql compressed format
    run(
        f"docker exec {container} pg_dump -U postgres -Fc -x -f {docker_dump_path} {dbname}"
    )
    get(host_dump_path, dump_file)
    sudo("rm {}".format(host_dump_path))


def dockergetdb(container="db_sblog", settings=None):
    "fetch and load remote database"
    dump_file = "sblog.dump"
    fetchdb()
    local("docker-compose up -d db_sblog")
    local(f'docker cp {dump_file} "$(docker-compose ps -q {container})":/{dump_file}')
    local(f"docker-compose exec {container} dropdb -U 'postgres' 'sblog' --if-exists")
    local(f"docker-compose exec {container} createdb -U 'postgres' 'sblog'")
    local(
        f"docker-compose exec {container} pg_restore -d 'sblog' -O {dump_file} -U 'postgres'"
    )
    local("rm " + dump_file)
