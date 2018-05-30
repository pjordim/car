import spade, sched, time
from threading import Timer
CMANAME = "cma@127.0.0.1"
CMAADDRESS = ["xmpp://cma@127.0.0.1"]
class CarAgent(spade.Agent.Agent):
	def __init__(self, agentjid, password):
		self.myAgent = spade.Agent.Agent.__init__(self, agentjid, password)
		self.sentRequest = False
		self.scheduler = sched.scheduler(time.time, time.sleep)

	
	def setSentRequestFalse(self):
		self.sentRequest = False


	def sendmsg(self):
		receiver = spade.AID.aid(name="cma@127.0.0.1", addresses=["xmpp://cma@127.0.0.1"])		
		# Second, build the message
		self.msg = spade.ACLMessage.ACLMessage()  # Instantiate the message
		self.msg.setPerformative("request")        # Set the "request" FIPA performative
		self.msg.setOntology("cmm")        # Set the ontology of the message content
		self.msg.setLanguage("OWL-S")	          # Set the language of the message content
		self.msg.addReceiver(receiver)            # Add the message receiver
		self.msg.setContent("Requesting change")
		# Third, send the message with the "send" method of the agent
		self.send(self.msg)
	

	def sendChangeRequest(self):
		if not self.sentRequest:
			#self.send(self.b.msg)
			self.sendmsg()
			self.sentRequest = True
			#self.scheduler.enter(1,1,self.setSentRequestFalse,())
			#self.setSentRequestFalse()
			t = Timer(2.0,self.setSentRequestFalse)
			t.start()
			#time.sleep(2)


	class RequestBehav(spade.Behaviour.OneShotBehaviour):
		
			
		def _process(self):
			# First, form the receiver AID
			receiver = spade.AID.aid(name="cma@127.0.0.1", 
                                     addresses=["xmpp://cma@127.0.0.1"])
			
			# Second, build the message
			self.msg = spade.ACLMessage.ACLMessage()  # Instantiate the message
			self.msg.setPerformative("request")        # Set the "request" FIPA performative
			self.msg.setOntology("cmm")        # Set the ontology of the message content
			self.msg.setLanguage("OWL-S")	          # Set the language of the message content
			self.msg.addReceiver(receiver)            # Add the message receiver
			self.msg.setContent("Requesting change")
			# Third, send the message with the "send" method of the agent
			self.CarAgent.send(self.msg)
			print 'msg sent from _process'


		# def sendChangeRequest(self):
		# 	if not self.sentRequest:
		# 		self.myAgent.send(self.msg)
		# 		self.sentRequest = True
		# 		s = sched.scheduler(time.time, time.sleep)
		# 		s.enter(5,1,self.sentRequestFalse(), self)

		
		

	def _setup(self):
		print "MyAgent starting . . ."
		b = self.RequestBehav()
		self.addBehaviour(b, None)

# if __name__ == "__main__":
# 	a = CarAgent("caragent@192.168.1.32", "secret")
# 	a.start()
		
