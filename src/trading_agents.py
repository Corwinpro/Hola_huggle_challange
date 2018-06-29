from pseudo_algo import Agent

counts = [1,2,3]
values1 = [1,3,1]
values2 = [2,4,0]
agent1 = Agent(counts, values1, 5, None)
agent2 = Agent(counts, values2, 5, None)

offer = agent1.offer(None)
print 'agent1: get ', offer
for i in range(5):
    offer_new = agent2.offer(offer)
    print 'agent2: get', offer_new
    if offer_new is None:
        print 'agreed.'
        print' Agent 1 gets ', agent1.offer_profit([counts[i] - offer[i] for i in range(len(counts))], values1)
        print' Agent 2 gets ', agent2.offer_profit(offer, values2)
        exit()
    offer = offer_new

    offer_new = agent1.offer(offer)
    print 'agent1: get', offer_new
    if offer_new is None:
        print 'agreed.'
        print' Agent 1 gets ', agent1.offer_profit(offer, values1)
        print' Agent 2 gets ', agent2.offer_profit([counts[i] - offer[i] for i in range(len(counts))], values2)
        exit()
    offer = offer_new