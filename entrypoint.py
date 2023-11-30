import tutake as tt

if __name__ == '__main__':
    tutake = tt.Tutake("./config.yml")
    tutake.task_api().start(True, True)
