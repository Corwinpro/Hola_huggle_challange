'use strict'; /*jslint node:true*/

module.exports = class Agent {
    constructor(me, counts, values, max_rounds, log){
        this.counts = counts;
        this.values = values;
        this.rounds = max_rounds;
        this.log = log;
        this.Total_value = this.inner(counts, values);
        [this.p2_set, this.p2_set_weights] = this.p2_values_set();
        this.hat_p2 = this.average_of_set(this.p2_set);
        this.p2_offers = [];
        this.my_offers = [];
        this.threshold = 5;
        this.reweighting_param = 0.1;
        //Optimal ofer J parameters
        this.diff_weight = 0.2;
        this.acceptance_threshold = 8.-this.diff_weight-0.05;

        this.offer_combinations = this.all_combinations(this.counts);
	}
	sum(a){
		var summ = 0;
        for (let i = 0; i<a.length; i++)
            summ += a[i];
        return summ;
	}
	inner(a,b){
		var inner = 0;
        for (let i = 0; i<a.length; i++)
            inner += a[i]*b[i];
        return inner;
	}
	all_combinations(A){
        var B = [];
        for (var i = 0; i <= A[0]; i++) {
            for (var j = 0; j <= A[1]; j++) {
              for (var k = 0; k <= A[2]; k++) {
                B.push([i, j, k]);
              }
            }
          }
        return B;
    }
    res_offer(o){
    /*Returns the residual of the offer,
    If I want o, the opponent gets res(o)*/
        var residual_offer = [];
        for (let i = 0; i<o.length; i++){
            residual_offer.push(this.counts[i] - o[i]);
        }
        return residual_offer;
    }
    offer_profit(o, value){
        return this.inner(o, value);
    }
    average_of_set(my_set){
    /*For a set my_set, we calculated the weighted average of values
    Example: Value(hat) = Summ of value_i(hat)*probability(value_i) / total_probability*/
        var average_set = [];
        for (let i = 0; i<this.values.length; i++){
            var _avg_value_i = 0.;
            for (let j = 0; j<my_set.length; j++){
                _avg_value_i += my_set[j][i]*this.p2_set_weights[j];
            }
            average_set.push(_avg_value_i/this.sum(this.p2_set_weights));
        }

        return average_set;
    }
    p2_values_set(){
        /*Given a list of counts, we find all possible admissible values,
        i.e. all lists V: (V,counts) == 10*/
        var max_prices = [];
        for (let i = 0; i< this.counts.length; i++)
            max_prices.push(Math.floor(10./this.counts[i]));
        var p2_set = [];
        var all_possible_prices = this.all_combinations(max_prices);
        for (let i = 0; i<all_possible_prices.length; i++){
            if (this.offer_profit(this.counts, all_possible_prices[i]) == this.Total_value){
                p2_set.push(all_possible_prices[i]);
            }
        }
        /*And assign initial weights for each set
        weight[i] == x: the values have x probability to appear in p2*/
        var p2_set_weights = [];
        for (let i = 0; i<p2_set.length; i++){
            p2_set_weights.push(1.)
        }
        return [p2_set, p2_set_weights];
    }
    update_p2_set(o){
        /*Given an offer o, we update the p2_set list*/
        this.p2_offers.push(o);
        /*by reweighting all entities which would result in low opponents profit,
        i.e. res == what opponent wants to get,
        if res.profit < self.threshold for v in p2_set, decrease probability(v)*/
        var res = this.res_offer(o);
        for (let i = 0; i<this.p2_set.length; i++){
            var value = this.p2_set[i];
            if (this.offer_profit(res, value) < this.threshold){
                this.p2_set_weights[i] *= this.reweighting_param;
            }
        }
        /*TODO
        Instead of 'dropping' the possible p2 values,
        It is worth to properly reweight the values list,
        e.g.: if for an item in p2_set we expect an offer to give X > threshold,
        the weight of the item is proportionally increased.
        Otherwise, it is decreased.
        Crude approximation, like X == 10: weight += 0.2
                                  X == 9: weight += 0.15,
                                  and so on 
        */
    }
    estimate_p2_profit(o){
        /*We estimate the expected opponents profit by average values of self.p2_set*/
        var average_p2_values = this.average_of_set(this.p2_set);
        var p2_profit = this.offer_profit(o, average_p2_values);
        return p2_profit;
    }
    J_ac(p1_profit, p2_profit){
        return p1_profit + this.diff_weight*(p1_profit - p2_profit);
    }
    proceed_offer(o){
        /*We calculate the internal acceptance cost function, J_ac.
        #If J_ac > self.acceptance_threshold, the offer is accepted*/
        var profit = this.offer_profit(o, this.values);
        if (profit > 9){
            return true;
        }
        var res = this.res_offer(o);
        var p2_profit = this.estimate_p2_profit(res);
        var proceed_to_accept = this.J_ac(profit, p2_profit) > this.acceptance_threshold;
        return proceed_to_accept;
        //Bug?
        /*if (proceed_to_accept){
            //print 'I get ', profit, 'and I expect to give ', p2_profit, ' with my estimation of values as ', self.hat_p2
            return proceed_to_accept;
        }*/
    }
    p2_acceptance_prob(o){
        var p2_profit = this.offer_profit(this.hat_p2, o);
        return Math.pow(p2_profit,0.9)/10.;
    }
    J_of(o){
        /*We dont accept offers with profit < 6*/
        if (this.inner(this.values, o) < 6.){
            return -1;
        }
        var res = this.res_offer(o);
        var J = this.p2_acceptance_prob(res) * (this.inner(this.values, o) + this.diff_weight*(this.inner(this.values, o) - this.inner(this.hat_p2, res)));
        return J;
    }
    generate_optimal_offer(){
        /*We generate the optimal offer o, which maximizes the J_of
        J_of = P(offer will be accepted)*self.J_ac
        The optimal o is given analytically*/
        var optimal_offer_J = 0.;
        var optimal_offer_index = 0;
        this.hat_p2 = this.average_of_set(this.p2_set);
        /*iterate through all possible offers and find the best one*/
        for (let i = 0; i<this.offer_combinations.length; i++){
            var current_offer_J = this.J_of(this.offer_combinations[i]);
            /*We give the same offer again ONLY if it's much more optimal than the rest*/
            if (this.my_offers.includes(this.offer_combinations[i])){
                current_offer_J *= 0.3;
            }
            if (current_offer_J > optimal_offer_J){
                optimal_offer_J = current_offer_J;
                optimal_offer_index = i;
            }
        }
        return this.offer_combinations[optimal_offer_index];
    }
    offer(o){
        this.log(`${this.rounds} rounds left`);
        this.rounds--;
        if (this.rounds < 3)
            this.acceptance_threshold -= 1.;
        if (o)
        {
            /*Given an offer, we process the new information: we update self.p2_set:*/
            this.update_p2_set(o);
            /*and calculate the acceptance cost function, J_ac,
            such that if J_ac == True, the offer is accepted,*/
            if (this.proceed_offer(o)){
                return;
            }
        }
        /*Otherwise, we generate an new offer by estimating an optimal offer*/
        var new_offer = this.generate_optimal_offer();
        this.my_offers.push(new_offer);
        /*And return the new offer*/
        return new_offer;
    }
};