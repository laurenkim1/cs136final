from graph import *
import operator
import random
import sys

# model skills using integers (money will be modeled using negative values)
NUM_SKILLS = 10
NUM_AGENTS = 10
SKILLS_PER_AGENT = 1

MAX_MONEY = 50
AGENTS_WITH_MONEY = 0.5
AGENTS_WANT_MONEY = 0.5


class Agent:
	def __init__(self, uid):
		self.UID = uid
		# time in marketplace - for ratings
		self.age = 0.0
		# dict of skill:rating (out of 5)
		self.skills = {}

	def get_UID(self):
		return self.UID

	def get_skills(self):
		return self.skills.keys()

	def offer_skill(self):
		# offer the skill with the highest rating
			# can also try skill with the most counts, or some combo of the two
		(skill_id, rating) = max(self.skills.iteritems(), key=lambda x: x[1])
		return skill_id

	# add skill to this agent's portfolio
	def add_skill(self, skill):
		if skill <= NUM_SKILLS:
			if skill not in self.skills:
				# (rating, number of ratings)
				self.skills[skill] = (5.0, 1)

	def get_skill_rating(self, skill):
		if skill in self.skills:
			return self.skills[skill]

	# update skill rating
	def update_skill(self, skill, newRating):
		if skill in self.skills:
			oldRating, count = self.skills[skill]
			# recompute new average rating
			self.skills[skill] = ((oldRating * count + newRating)/(count + 1), count+1)


class MarketPlace:
	def __init__(self):
		# list of (agent, want, offer)
		self.graph = []
		# dict of agent's UID: agent object
		self.agents = {}

	def register_agent(self, agent):
		uid = agent.get_UID()
		self.agents[uid] = agent

	# agent wants to trade services in next matching 
	# round of the market
	def enter_market(self, agent, want, offer):
		uid = agent.get_UID()
		# check agent has the skill he offers
		if offer in agent.skills:
			self.graph.append((uid, want, offer))

	# agent no longer wants to trade in next matching
	# round of the market
	def leave_market(self, agent, want, offer):
		return

	# order the agents offering the same skill based on their ratings
	# best to worst
	# dict of string:list = {skill: [agents UIDs ordered best to worst rating]}
	def rank_agents(self):
		desiredSkills = set([x[1] for x in self.graph])
		skillToOrdering = {}
		for skill in desiredSkills:
			agents = []

			# if wanted skill is a service
			if skill >= 0:
				for node in self.graph:
					if node[2] == skill:
						uid = node[0]
						agent = self.agents[uid]
						rating = agent.get_skill_rating(skill)
						agents.append((uid, rating))

			# if wanted skill is money
			elif skill < 0:
				for node in self.graph:
					if node[2] < skill:
						uid = node[0]
						# agent willing to pay more (value is more negative) than provider wants
						# use price as rating
						rating = -1 * node[2]
						agents.append((uid, rating))

			agents = sorted(agents, key=lambda x: x[1], reverse=True)
			skillToOrdering[skill] = agents
		return skillToOrdering


	# call to make a TTC matching on existing agents in graph so far
	# return allocation and
	# clear out matched agents from graph
	def make_match(self):
		# dict of string:list = {skill: [agents UIDs ordered best to worst rating]}
		skillToOrdering = self.rank_agents()

		# list of UIDs of participating agents
		participatingAgents = [x[0] for x in self.graph]
		# dict of {agent UIDs:agent UIDs}
		initialOwnership = {}
		for node in self.graph:
			if node[2] in initialOwnership:
				initialOwnership[node[2]].append(node[0])
			else:
				initialOwnership[node[2]] = [node[0]]

		# agentPreferences is a dictionary with keys being agents and values being
		# lists that are permutations of the list of all houses.
		agentPreferences = {}
		for node in self.graph:
			desiredSkill = node[1]
			agentPrefOrdering = skillToOrdering[desiredSkill]
			# add each agent to the end of their own preference ordering
			agentPrefOrdering.append((node[0], (5.0,1)))
			agentPreferences[node[0]] = agentPrefOrdering

		offeredSkills = {}
		for node in self.graph:
			offeredSkills[node[0]] = node[2]

		return topTradingCycles(participatingAgents, offeredSkills, agentPreferences, initialOwnership)



########################
# TTC stuff. Modified code from:
# https://github.com/j2kun/top-trading-cycles/blob/master/toptradingcycles.py
########################

# getAgents: graph, vertex -> set(vertex)
# get the set of agents on a cycle starting at the given vertex
def getAgents(G, cycle, agents):
   # a cycle in G is represented by any vertex of the cycle
   # outdegree guarantee means we don't care which vertex it is

   # make sure starting vertex is a house
   if cycle.vertexId in agents:
      cycle = cycle.anyNext()

   currentVertex = cycle
   theAgents = set()

   while currentVertex not in theAgents:
      theAgents.add(currentVertex)
      currentVertex = currentVertex.anyNext()

   return theAgents


# anyCycle: graph -> vertex
# find any vertex involved in a cycle
def anyCycle(G):
   visited = set()
   v = G.anyVertex()
   while v not in visited:
      visited.add(v)
      v = v.anyNext()
   return v


# find a core matching of agents to houses
# agents and houses are unique identifiers for the agents and houses involved
# agentPreferences is a dictionary with keys being agents and values being
# lists that are permutations of the list of all houses.
# initiailOwnerships is a dict {houses:agents}
def topTradingCycles(agents, houses, agentPreferences, initialOwnership):
   # form the initial graph
   average_pref_granted = 0
   agents = set(agents)
   vertexSet = set(agents)
   G = Graph(vertexSet)

   # maps agent to an index of the list agentPreferences[agent]
   currentPreferenceIndex = dict()
   for a in agents:
       currentPreferenceIndex[a] = 0

   preferredAgent = lambda a: agentPreferences[a][currentPreferenceIndex[a]][0]

   for a in agents:
    # add an edge to agent's most desired peer to complete task
    G.addEdge(a, preferredAgent(a))

   # iteratively remove top trading cycles
   allocation = dict()
   num_exchanges = 0
   while len(G.vertices) > 0:
      cycle = anyCycle(G)
      cycleAgents = getAgents(G, cycle, agents)

      # assign agents in the cycle their house
      for a in cycleAgents:
      	 average_pref_granted += currentPreferenceIndex[a.vertexId]
         assigned_agent = a.anyNext().vertexId
         allocation[a.vertexId] = assigned_agent
         if a.vertexId != assigned_agent:
         	num_exchanges += 1
         
      for a in cycleAgents:
      	G.delete(a)

      for a in agents:
         if a in G.vertices and G[a].outdegree() == 0:
            while preferredAgent(a) not in G.vertices:
               currentPreferenceIndex[a] += 1
            G.addEdge(a, preferredAgent(a))

   return (num_exchanges, average_pref_granted / len(agents), allocation)

########################
# Back to our own code #
########################

def one_trial():
	# initialize market
	mkt = MarketPlace()

	# initialize M agents
	random.seed()
	all_agents = []
	for i in range(NUM_AGENTS):
		new_agent = Agent(i)
		total = 0
		# randomly assign some agents money as a skill
		if random.random() < AGENTS_WITH_MONEY:
			new_skill = -1 * random.randint(1,MAX_MONEY)
			new_agent.add_skill(new_skill)
			total = 1
		# give each agent SKILLS_PER_AGENT random service skills
		for j in range(SKILLS_PER_AGENT - total):
			new_skill = random.randint(1,NUM_SKILLS)
			new_agent.add_skill(new_skill)
		
		all_agents.append(new_agent)

		# register agent in the market
		mkt.register_agent(new_agent)

		# pick a skill for the agent to offer
		offer = new_agent.offer_skill()

		# randomly pick a want from all skills (and money) that are not agent's skills
		agent_skills = new_agent.get_skills()

		want = agent_skills[0]
		while want in agent_skills:
			# agents want a skill that they don't have
			want = random.randint(1, NUM_SKILLS)

			# some proportion of agents want money, unless their offer is money
			if want > 0:
				if random.random() < AGENTS_WANT_MONEY:
					want = -1 * random.randint(1, MAX_MONEY)
	
		mkt.enter_market(new_agent, want, offer)

	# once all agents registered, run TTC
	return mkt.make_match()




def main():
	num_iterations = int(sys.argv[1])
	avg_exchanges = 0
	avg_pref_overall = 0
	for i in range(num_iterations):
		(exchanges, avg_pref, alloc) = one_trial()
		avg_exchanges += exchanges
		avg_pref_overall += avg_pref
	avg_exchanges = avg_exchanges / num_iterations
	avg_pref_overall = avg_pref_overall / num_iterations

	print "On average, ", avg_exchanges, " / ", NUM_AGENTS, " were included"
	print "On average, user got ", avg_pref_overall, "th preference overall (zero-indexed)"


def test_1():
	# initialize market
	mkt = MarketPlace()

	# initialize 2 agents
	agent_1 = Agent(0)
	agent_1.add_skill(1)
	mkt.register_agent(agent_1)

	agent_2 = Agent(1)
	agent_2.add_skill(2)
	mkt.register_agent(agent_2)

	mkt.enter_market(agent_1, 2, 1)
	mkt.enter_market(agent_2, 1, 2)

	print "Agent 1 wants 2, offers 1. Agent 2 wants 1, offers 2."
	print "Expecting 2 exchanged agents..."

	# once all agents registered, run TTC
	(num_exchanges, avg_pref, alloc) = mkt.make_match()

	print "average pref granted: ", avg_pref
	print alloc

	if not num_exchanges == 2:
		raise AssertionError()

def test_2():
	# initialize market
	mkt = MarketPlace()

	# initialize 2 agents
	agent_1 = Agent(0)
	agent_1.add_skill(1)
	mkt.register_agent(agent_1)

	agent_2 = Agent(1)
	agent_2.add_skill(2)
	mkt.register_agent(agent_2)

	agent_3 = Agent(2)
	agent_3.add_skill(3)
	mkt.register_agent(agent_3)

	agent_4 = Agent(3)
	agent_4.add_skill(4)
	mkt.register_agent(agent_4)

	mkt.enter_market(agent_1, 2, 1)
	mkt.enter_market(agent_2, 3, 2)
	mkt.enter_market(agent_3, 4, 3)
	mkt.enter_market(agent_4, 1, 4)

	print "Expecting 4 exchanged agents..."

	# once all agents registered, run TTC
	(num_exchanges, avg_pref, alloc) = mkt.make_match()

	print "average pref granted: ", avg_pref
	print alloc

	if not num_exchanges == 4:
		raise AssertionError()

#test_1()
#test_2()
main()



