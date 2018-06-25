#TODO
#   p2_set:
#       No need in the set. Only need the \hat{p2_set}
#   generate_optimal_offer:
#       Need analytical expression and linear solver

class Agent():
    def __init__(self, counts, values, max_rounds, log):
        self.counts = counts
        self.values = values
        self.rounds = max_rounds
        self.log = log
        self.total = 0
        for i in range(len(self.counts)): 
            self.total += counts[i]*values[i]
        self.p2_set, self.p2_set_weights = self.p2_values_set()
        self.p2_offers = []
        self.my_offers = []
        self.threshold = 5
        self.reweighting_param = 0.5
        self.Total_value = 10
        #Optimal ofer J parameters
        self.acceptance_threshold = 8.
        self.diff_weight = 0.2

    def offer_profit(self, o, value):
        profit = 0
        for i in range(len(o)):
            profit += o[i]*value[i]

    def average_of_set(self, my_set):
        #For a set my_set, we calculated the weighted average of values
        #Example: Value(hat) = Summ of value_i(hat)*probability(value_i) / total_probability
        average_set = []
        for i in range(len(self.values)):
            _avg_value_i = 0.
            for j in range(len(my_set)):
                _avg_value_i += my_set[j][i]*self.p2_set_weights[j]
            average_set.append(_avg_value_i/sum(self.p2_set_weights))
        return average_set

    def p2_values_set(self):
        #Given a list of counts, we find all possible admissible values,
        #i.e. all lists V: (V,counts) == 10
        p2_set = [[0. for i in range(len(self.values))] for j in range(5)]
        self.default_p2_set = self.average_of_set(p2_set)
        #And assign initial weights for each set
        #weight[i] == x: the values have x probability to appear in p2
        p2_set_weights = [1. for i in range(len(self.values))]
        return (p2_set, p2_set_weights)

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
        p2_profit = self.estimate_p2_profit(o)
        return self.J_ac(profit, p2_profit) > self.acceptance_threshold

    def generate_optimal_offer(self):
        #We generate the optimal offer o, which maximizes the J_of
        #J_of = P(offer will be accepted)*self.J_ac
        #The optimal o is given analytically
        return

    def offer(self, o):
        self.log("{0} rounds left".format(self.rounds))
        self.rounds= self.rounds - 1
        if (o):
            self.p2_offers.append(o)
            #Given an offer, we calculate the acceptance cost function, J_ac,
            #such that if J_ac == True, the offer is accepted,
            if self.proceed_offer(o):
                return
        
        #otherwise, we process the new information: we update self.p2_set:
        #we remove the 'bad' opponent's values from the self.p2_set
        self.update_p2_set(o)
        #Then, we generate an new optimal offer
        new_offer = self.generate_optimal_offer()
        self.my_offers.append(new_offer)
        #And return the new offer
        return new_offer
