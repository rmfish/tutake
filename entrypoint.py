import tutake as tt
from tutake.remote.server import RemoteServer

if __name__ == '__main__':
    tutake = tt.Tutake("./config.yml")
    RemoteServer(tutake).start(True)
    tutake.task_api().start(True)
