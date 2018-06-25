class Agent():
    def __init__(self, counts, values, max_rounds, log):
        self.counts = counts
        self.values = values
        self.rounds = max_rounds
        self.log = log
        self.Total_value = 0
        for i in range(len(self.counts)): 
            self.Total_value += counts[i]*values[i]
        self.p2_set, self.p2_set_weights = self.p2_values_set()
        self.default_p2_set = self.average_of_set(self.p2_set)
        self.p2_offers = []
        self.my_offers = []
        self.threshold = 5
        self.reweighting_param = 0.1
        #Optimal ofer J parameters
        self.diff_weight = 0.5
        self.acceptance_threshold = 8.-self.diff_weight-0.05

        self.offer_combinations = self.all_combinations(self.counts)

        #agent = Agent([1,2,3], [0,2,2], 1, None)
        #print agent.offer([1,2,0])

    def sum(self, a):
        summ = 0
        for i in range(len(a)):
            summ += a[i]
        return summ
   
    def inner(self, a, b):
        summ = 0
        for i in range(len(a)):
            summ += a[i]*b[i]
        return summ
    
    def offer_profit(self, o, value):
        return self.inner(o, value)

    def average_of_set(self, my_set):
        #For a set my_set, we calculated the weighted average of values
        #Example: Value(hat) = Summ of value_i(hat)*probability(value_i) / total_probability
        average_set = []
        for i in range(len(self.values)):
            _avg_value_i = 0.
            for j in range(len(my_set)):
                _avg_value_i += my_set[j][i]*self.p2_set_weights[j]
            average_set.append(_avg_value_i/self.sum(self.p2_set_weights))
        return average_set

    def p2_values_set(self):
        #Given a list of counts, we find all possible admissible values,
        #i.e. all lists V: (V,counts) == 10
        max_prices = [int(10./self.counts[i]) for i in range(len(self.counts))]
        p2_set = []
        all_possible_prices = self.all_combinations(max_prices)
        for price in all_possible_prices:
            #print self.offer_profit(self.counts, price)
            if self.offer_profit(self.counts, price) ==  self.Total_value:
                p2_set.append(price)
        #And assign initial weights for each set
        #weight[i] == x: the values have x probability to appear in p2
        p2_set_weights = [1. for i in range(len(p2_set))]
        return p2_set, p2_set_weights

    def update_p2_set(self, o):
        #Given an offer o, we update the p2_set list
        #by reweighting all entities which would result in low opponents profit,
        #i.e. if o.profit < self.threshold for v in p2_set, decrease probability(v)
        for i in range(len(self.p2_set)):
            value = self.p2_set[i]
            if self.offer_profit(o, value) < self.threshold:
                self.p2_set_weights[i] *= self.reweighting_param

    def estimate_p2_profit(self, o):
        #We estimate the expected opponents profit by average values of self.p2_set
        average_p2_values = self.average_of_set(self.p2_set)
        p2_profit = self.offer_profit(o, average_p2_values)
        return p2_profit

    def J_ac(self, p1_profit, p2_profit):
        return p1_profit + self.diff_weight*(p1_profit - p2_profit)

    def proceed_offer(self, o):
        #We calculate the internal acceptance cost function, J_ac.
        #If J_ac > self.acceptance_threshold, the offer is accepted
        profit = self.offer_profit(o, self.values)
        if profit > 9:
            return True
        p2_profit = self.estimate_p2_profit(o)
        proceed_to_accept = self.J_ac(profit, p2_profit) > self.acceptance_threshold
        if proceed_to_accept:
            print 'I get ', profit, 'and I expect him to get ', p2_profit
        return proceed_to_accept
    
    def all_combinations(self, A):
        B = [[]]
        for t in [range(e+1) for e in A]:
                B = [x+[y] for x in B for y in t]
        return B

    def p2_acceptance_prob(self, o):
        p2_profit = self.offer_profit(self.hat_p2, o)
        #return p2_profit**0.8 / 10.
        if p2_profit >= 9.:
            return 1.
        elif p2_profit <= 4.:
            return 0.1
        else:
            return 0.18*p2_profit - 0.62

    def J_of(self, o):
        #We dont accept offers with profit < 6
        if self.inner(self.values, o) < 6.:
            return -1
        #P2 gets res = Total - my_offer
        res = [self.counts[i] - o[i] for i in range(len(self.counts))]
        J = self.p2_acceptance_prob(res) * (self.inner(self.values, o) + 
                                                self.diff_weight*(self.inner(self.values, o) 
                                                                - self.inner(self.hat_p2, res)))
        return J

    def generate_optimal_offer(self):
        #We generate the optimal offer o, which maximizes the J_of
        #J_of = P(offer will be accepted)*self.J_ac
        #The optimal o is given analytically
        optimal_offer_J = 0.
        optimal_offer_index = 0
        self.hat_p2 = self.average_of_set(self.p2_set)
        #iterate through all possible offers and find the best one
        for i in range(len(self.offer_combinations)):
            current_offer_J = self.J_of(self.offer_combinations[i])
            if self.offer_combinations[i] in self.my_offers:
                current_offer_J *= 0.3
            if current_offer_J > optimal_offer_J:
                optimal_offer_J = current_offer_J
                optimal_offer_index = i
        return self.offer_combinations[optimal_offer_index]

    def offer(self, o):
        #self.log("{0} rounds left".format(self.rounds))
        self.rounds= self.rounds - 1
        if (o):
            self.p2_offers.append(o)
            #Given an offer, we calculate the acceptance cost function, J_ac,
            #such that if J_ac == True, the offer is accepted,
            if self.proceed_offer(o):
                return
            #otherwise, we process the new information: we update self.p2_set:
            self.update_p2_set(o)
        
        #Then, we generate an new optimal offer
        new_offer = self.generate_optimal_offer()
        self.my_offers.append(new_offer)
        #And return the new offer
        return [self.counts[i] - new_offer[i] for i in range(len(self.counts))]

counts = [1,6,2]
values1 = [2,1,1]
values2 = [0,1,2]
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
