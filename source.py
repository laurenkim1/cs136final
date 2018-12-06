from graph import *
import operator


# just to make sure skill listings are standardized
skillDict = {
	"Money": "Money",
	"Python": "Python",
	"Baby Sitting": "Baby Sitting",
	"": "",
	"": "",
	"": "",
}


class Agent:
	def __init__(self, uid):
		self.UID = uid
		# time in marketplace - for ratings
		self.age = 0.0
		# dict of skill:rating (out of 5)
		self.skills = {}

	def get_UID(self):
		return self.UID

	# add skill to this agent's portfolio
	def add_skill(self, skill):
		if skill in skillDict:
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
			self.skills[skill] = ((oldRating + newRating)/count, count+1)


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
			self.graph.append(uid, want, offer)

	# agent no longer wants to trade in next matching
	# round of the market
	def leave_market(self, agent, want, offer):

	# order the agents offering the same skill based on their ratings
	# best to worst
	# dict of string:list = {skill: [agents UIDs ordered best to worst rating]}
	def rank_agents():
		desiredSkills = set([x[1] for x in self.graph])
		skillToOrdering = {}
		for skill in desiredSkills:
			agents = []
			for node in self.graph:
				if node[2] = skill:
					uid = agent.get_UID()
					rating = agent.get_skill_rating(skill)
					agents.append(uid, rating)
			agents.sort(operator.itemgetter(1), reverse=True)
			skillToOrdering[skill] = agents
		return skill_to_ordering


	# call to make a TTC matching on existing agents in graph so far
	# return allocation and
	# clear out matched agents from graph
	def make_match(self):
		# dict of string:list = {skill: [agents UIDs ordered best to worst rating]}
		skillToOrdering = self.rank_agents()
		# list of UIDs of participating agents
		participatingAgents = [x[0] for x in self.graph]
		# dict of {offeredSkills:agents}
		initialOwnership = {}
		for node in self.graph:
			offeredSkillRank = skillToOrdering[node[2]].index(node[0])
			# if agent "1" is 3rd best at "Python" then
			# uniqueRankedSkill = "Python2" (because index 2)
			uniqueRankedSkill = node[2]+str(offeredSkillRank)
			# "Python2": "1"
			initialOwnership[uniqueRankedSkill] = node[0]

		# agentPreferences is a dictionary with keys being agents and values being
		# lists that are permutations of the list of all houses.
		agentPreferences = {}
		for node in self.graph:
			agentPreferences[node[0]] = 

		alloc = topTradingCycles(participatingAgents, skills, agentPreferences, initialOwnership)



########################
# TTC stuff
# following code from: https://github.com/j2kun/top-trading-cycles/blob/master/toptradingcycles.py
########################

# getAgents: graph, vertex -> set(vertex)
# get the set of agents on a cycle starting at the given vertex
def getAgents(G, cycle, agents):
   # a cycle in G is represented by any vertex of the cycle
   # outdegree guarantee means we don't care which vertex it is

   # make sure starting vertex is a house
   if cycle.vertexId in agents:
      cycle = cycle.anyNext()

   startingHouse = cycle
   currentVertex = startingHouse.anyNext()
   theAgents = set()

   while currentVertex not in theAgents:
      theAgents.add(currentVertex)
      currentVertex = currentVertex.anyNext()
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
   agents = set(agents)
   vertexSet = set(agents) | set(houses)
   G = Graph(vertexSet)

   # maps agent to an index of the list agentPreferences[agent]
   currentPreferenceIndex = dict((a,0) for a in agents)
   preferredHouse = lambda a: agentPreferences[a][currentPreferenceIndex[a]]

   for a in agents:
      G.addEdge(a, preferredHouse(a))
   for h in houses:
      G.addEdge(h, initialOwnership[h])

   # iteratively remove top trading cycles
   allocation = dict()
   while len(G.vertices) > 0:
      cycle = anyCycle(G)
      cycleAgents = getAgents(G, cycle, agents)

      # assign agents in the cycle their house
      for a in cycleAgents:
         h = a.anyNext().vertexId
         allocation[a.vertexId] = h
         G.delete(a)
         G.delete(h)

      for a in agents:
         if a in G.vertices and G[a].outdegree() == 0:
            while preferredHouse(a) not in G.vertices:
               currentPreferenceIndex[a] += 1
            G.addEdge(a, preferredHouse(a))

   return allocation

