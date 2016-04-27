import he10_fridge_control.control.lakeshore as LS

# setup thermometry
ChaseLS = LS.Lakeshore350('192.168.0.12',  ['UC Head', 'IC Head', 'UC stage', 'LC shield'])

ChaseLS.set_heater_range(1, 0)
