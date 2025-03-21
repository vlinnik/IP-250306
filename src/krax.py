from pyplc.config import plc
from project import name as project_name, version_short as project_version
from concrete import Factory,Weight,Container,Lock,Dosator,Mixer,MSGate,Motor,Manager,Readiness,Loaded,FlowMeter
from concrete.elevator import ElevatorGeneric
from concrete.imitation import iMOTOR,iGATE,iWEIGHT,iVALVE,iELEVATOR,iROTARYFLOW
from pyplc.utils.misc import BLINK
import sys

print('\tStarting PLC for project %s version %s' % (project_name, project_version))

factory_1 = Factory()

cement_m_1 = Weight(raw = plc.CEMENT_M_1, mmax = 1500)
silage_1 = Container( m = lambda: cement_m_1.m, out = plc.AUGER_ON_1, lock = Lock(key=~plc.DCEMENT_CLOSED_1) )
dcement_1 = Dosator( m = lambda: cement_m_1.m, closed = plc.DCEMENT_CLOSED_1, out = plc.DCEMENT_OPEN_1, lock = Lock(key=lambda: plc.AUGER_ON_1 or not plc.MIXER_ISON_1 ),containers=[silage_1] )

aerator_1 = BLINK(enable=plc.AUGER_ON_1, q = plc.AERATOR_ON_1, t_off = 3000 )

water_m_1 = Weight(raw = plc.WATER_M_1, mmax = 500)
water_1 = Container( m = lambda: water_m_1.m, out = plc.WPUMP_ON_1, lock = Lock(key=~plc.DWATER_CLOSED_1) )
dwater_1 = Dosator( m = lambda: water_m_1.m, closed = plc.DWATER_CLOSED_1, out = plc.DWATER_OPEN_1, lock = Lock(key=lambda: plc.WPUMP_ON_1 or not plc.MIXER_ISON_1 ),containers=[water_1] )

addition_1 = FlowMeter(out=plc.APUMP_ON_1,cnt=plc.ADDITION_Q_1,impulseWeight=0.01,closed=True)

fillers_m_1 = Weight(raw=plc.CONVEYOR_M_1, mmax = 8000)
filler_1 = Container(m = lambda: fillers_m_1.m, out=plc.FILLER_OPEN_1, lock = Lock(key=lambda: plc.FILLER_OPEN_2 or plc.CONVEYOR_ON_1 ))
filler_2 = Container(m = lambda: fillers_m_1.m, out=plc.FILLER_OPEN_2, lock = Lock(key=lambda: plc.FILLER_OPEN_1 or plc.CONVEYOR_ON_1 ))
dfillers_1 = Dosator(m = lambda: fillers_m_1.m, out=plc.CONVEYOR_ON_1, containers=[filler_1,filler_2],lock=Lock(key=lambda: plc.FILLER_OPEN_1 or plc.FILLER_OPEN_2 or not plc.ELEVATOR_BELOW_1 ))

elevator_1 = ElevatorGeneric(above=plc.ELEVATOR_ABOVE_1,below = plc.ELEVATOR_BELOW_1, middle = plc.ELEVATOR_MIDDLE_1,up = plc.ELEVATOR_UP_1, down=plc.ELEVATOR_DOWN_1, containers = [filler_1,filler_2],dosator = dfillers_1)

gate_1 = MSGate( closed = plc.MIXER_CLOSED_1, opened = plc.MIXER_OPENED_1,open=plc.MIXER_OPEN_1)
motor_1 = Motor( ison = plc.MIXER_ISON_1, powered = plc.MIXER_ON_1)
mixer_1 = Mixer( gate=gate_1, motor = motor_1,flows=[ x.q for x in [silage_1,water_1,addition_1,filler_1,filler_2] ] )

addition_1.install_counter( lambda: mixer_1.qreset )

factory_1.on_mode = [ x.switch_mode for x in [silage_1,water_1,filler_1,filler_2,dcement_1,dwater_1,dfillers_1,addition_1] ]
factory_1.on_emergency = [x.emergency for x in [silage_1,water_1,filler_1,filler_2,dcement_1,dwater_1,dfillers_1,mixer_1,elevator_1,addition_1] ]

def loadOrder_1():
  elevator_1.unload = True
  while not elevator_1.unloaded and not elevator_1.above: yield 
  dcement_1.unload = True
  dwater_1.unload = True
  addition_1.go = True
  yield
  addition_1.go = False
    
ready_1 = Readiness([dcement_1,dwater_1,elevator_1]) #что должно быть loaded перед началом загрузки в смеситель
loaded_1 = Loaded([dcement_1,dwater_1,elevator_1,addition_1])  #что должно быть unloaded чтобы смеситель считать загруженным
manager_1 = Manager(collected=ready_1,loaded=loaded_1,mixer=mixer_1,dosators=[dcement_1,dwater_1,dfillers_1,elevator_1],loadOrder= loadOrder_1)  #dosators= кому надо установить unload для начала загрузки

instances = [ factory_1,gate_1,motor_1,mixer_1,cement_m_1,silage_1,dcement_1,water_m_1,water_1,dwater_1, fillers_m_1,filler_1,filler_2,dfillers_1,elevator_1,ready_1,loaded_1,manager_1,addition_1,aerator_1 ]

if sys.platform=='linux':
  if sys.platform=='linux':
    import argparse
    from pyplc.config import exports
    args = argparse.ArgumentParser(sys.argv)
    args.add_argument('--exports',action='store_true')
    ns = args.parse_args()
    if ns.exports:
      exports(ctx=globals())
      sys.exit(0)
      
  imotor_1 = iMOTOR(simple=True,on=plc.MIXER_ON_1,ison=plc.MIXER_ISON_1)
  igate_1 = iGATE(open = plc.MIXER_OPEN_1,close=~plc.MIXER_OPEN_1,opened = plc.MIXER_OPENED_1,closed=plc.MIXER_CLOSED_1)  
  
  idcement_1 = iVALVE(open = plc.DCEMENT_OPEN_1,closed = plc.DCEMENT_CLOSED_1)
  isilage_1 = iMOTOR(simple=True, on = plc.AUGER_ON_1,ison = plc.AUGER_ISON_1)
  icement_m_1 = iWEIGHT( loading=plc.AUGER_ON_1,unloading=plc.DCEMENT_OPEN_1, q = plc.CEMENT_M_1 )
  
  idwater_1 = iVALVE(open = plc.DWATER_OPEN_1,closed = plc.DWATER_CLOSED_1)
  iwater_1 = iMOTOR(simple=True, on = plc.WPUMP_ON_1,ison = plc.WPUMP_ISON_1)
  iwater_m_1 = iWEIGHT( loading=plc.WPUMP_ON_1,unloading=plc.DWATER_OPEN_1, q = plc.WATER_M_1 )
  
  iapump_1 = iMOTOR(simple=True,on=plc.APUMP_ON_1,ison=plc.APUMP_ISON_1 )

  idfillers_1 = iMOTOR(simple=True,on = plc.CONVEYOR_ON_1,ison = plc.CONVEYOR_ISON_1 )
  ifillers_m_1 = iWEIGHT( loading=lambda: plc.FILLER_OPEN_1 or plc.FILLER_OPEN_2,unloading=plc.CONVEYOR_ON_1, q = plc.CONVEYOR_M_1 )
  
  # iaddition_1_q = iROTARYFLOW( loading=plc.APUMP_ON_1,q = plc.ADDITION_Q_1)
  
  ielevator_1 = iELEVATOR( up=plc.ELEVATOR_UP_1, down=plc.ELEVATOR_DOWN_1, above=plc.ELEVATOR_ABOVE_1,below = plc.ELEVATOR_BELOW_1,middle=plc.ELEVATOR_MIDDLE_1 )

  instances += [imotor_1,igate_1,idcement_1,isilage_1,icement_m_1,idwater_1,iwater_1,iwater_m_1,idfillers_1,ifillers_m_1,ielevator_1,iapump_1]
  

plc.run( instances=instances, ctx=globals() )
