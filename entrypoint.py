import tutake as tt
from tutake.remote.server import TutakeServer

if __name__ == '__main__':
    tutake = tt.Tutake("./config.yml")
    # TutakeServer(tutake).start()
    tutake.task_api().start(False)
