#!/usr/bin/env python
# encoding: utf-8
"""
Author: Amie Settlecowski
Version: 1.0
Date: 4 May 2016
Software project developed during BIOL7800 Programming for Biologists (Brant
Faircloth) at Louisiana State University.

This script is a component of the Simple ABC Tutorial. Specifically it defines
the class AbcBin implemented in the tutorial via tutorial.py.
"""
import random
import numpy
from scipy import stats
from matplotlib import pyplot
from matplotlib import lines


class AbcBin():
    ''' This class specifies objects that have attributes and methods that
        enable simple estimation of the mean of a binomial via ABC '''
    def __init__(self,
                 p,
                 N,
                 sample_size,
                 posterior_size,
                 method='rej',
                 sumstat='mean'):
        self.parent_p = p
        self.parent_N = N
        self.sample_size = sample_size
        self.posterior_size = posterior_size
        self.method = method
        self.sumstat = sumstat
        self.parent_dist = stats.binom(N, p)
        # Generate 'observed' dataset, the sample of the true 'parent'
        # distribution whose mean we are attempting to estimate
        self.observed_data = self.parent_dist.rvs(size=sample_size)
        self.epsilon = self.observed_data.std()
        self.posterior = {'parameter': [], 'stat': []}
        self.rejected = {'parameter': [], 'stat': []}

    def _reject(self, obs, sim, e, method='rej'):
        ''' Calculates some measure of distance between observed and simulated
            summary statistics and compares with the threshold, e, using the
            comparison method specified. Returns True when the distance is
            greater than e.'''
        if method == 'rej':
            if abs(obs - sim) > e:
                return True
            else:
                return False
        if method == 'lin':
            ''' *** In progress *** Ultimately this function will also
            implement linear approximation of the rejection algorithm as a
            comparison method option.'''
            pass

    def _sample_prior(self, lower, upper):
        ''' Randomly draw p from flat prior distribution.'''
        return random.uniform(lower, upper)

    def _calc_sumstat(self, data, sumstat):
        ''' Calculates user specified summary statistic for observed and each
            iteratively simulated dataset '''
        if sumstat == 'mean':
            return data.mean()
        elif sumstat == 'mode':
            return stats.mode(data)[0][0]
        elif sumstat == 'median':
            return numpy.median(data)

    def _estimate(self):
        '''Generates posterior distribution of p based on object specifications,
           populating the attribute dictionaries posterior and rejected.'''
        post_n = self.posterior_size
        sample_n = self.sample_size
        parent_n = self.parent_N
        e = self.epsilon
        obs_data = self.observed_data
        method = self.method
        stat = self.sumstat
        obs_stat = self._calc_sumstat(obs_data, stat)
        count = {'posterior': 0, 'steps': 0}
        while count['posterior'] < post_n:
            p_est = self._sample_prior(0.0, 1.0)
            # Simulate dataset by defining distriubtion with p_est
            # and drawing random sample
            sim_data = numpy.random.binomial(parent_n, p_est, size=sample_n)
            sim_stat = self._calc_sumstat(sim_data, stat)
            # Compare summary statistic from simulated data to observed data
            if self._reject(obs_stat, sim_stat, e, method):
                self.rejected['stat'].append(sim_stat)
            else:
                # Collect in posterior distribution if accepted
                self.posterior['parameter'].append(p_est)
                self.posterior['stat'].append(sim_stat)
                count['posterior'] += 1
            # Exit while loop once we have generated a posterior distribution
            # of p of specified size
            count['steps'] += 1

    def _select(self):
        """ ***In progress*** Ultimately will implement model selection between
            binomial and normal 'models' for estimating mu"""
        pass

    def run(self, application='estimate'):
        ''' Coordinates the steps of ABC to complete estimation of p'''
        if application == 'estimate':
            self._estimate()
        elif application == 'select':
            """ ***In progress*** Ultimately user will be able to specify
            whether they are estimating a parameter under 1 model,
            or comparing estimation between models. """
            self._select()

    def display_parent(self):
        ''' Returns figure summarizing the true 'parent' distribution whose
            mean we are estimating. '''
        figure = pyplot.figure()
        x = numpy.linspace(0, self.parent_N, (self.parent_N + 1))
        pmf = stats.binom.pmf(x, self.parent_N, self.parent_p)
        pyplot.plot(x, pmf, color='black', lw=2, linestyle='dashed', alpha=0.4)
        pyplot.vlines(x, 0, pmf, color='g', lw=10, alpha=0.8)
        pyplot.xlabel('x (binomial random variable)')
        pyplot.ylabel('probability')
        pyplot.suptitle('x ~ bin(n = {}, p = {})'.format(self.parent_N, self.parent_p),
                        fontsize=18, fontweight='bold', y=1)
        pyplot.title('Binomial distribution PMF (probability mass function)',
                      fontsize=14)
        return figure

    def display_sumstats(self):
        ''' Returns figure summarizing the accepted and rejected summary
            statistics. '''
        figure = pyplot.figure()
        acc_array = numpy.array(self.posterior['stat'])
        rej_array = numpy.array(self.rejected['stat'])
        bins = numpy.linspace(rej_array.min(), rej_array.max(), 100)
        pyplot.hist(rej_array, bins, color='red', alpha=0.4)
        red_line = lines.Line2D([], [], color='red', marker='_',
                                markersize=10, label='rejected')
        pyplot.hist(acc_array, bins, color='green', alpha=.8)
        green_line = lines.Line2D([], [], color='green', marker='_',
                                  markersize=10, label='accepted')
        pyplot.legend(handles=[red_line, green_line])
        pyplot.xlabel('{} (summary statistic)'.format(self.sumstat))
        pyplot.ylabel('frequency')
        return figure

    def display_posterior(self):
        ''' Returns figure summarizing the posterior distribution of p.'''
        figure = pyplot.figure()
        acc_array = numpy.array(self.posterior['parameter'])
        bins = numpy.linspace(0.0, 1.0, 100)
        pyplot.hist(acc_array, bins, facecolor='green', alpha=.8)
        x = numpy.linspace(stats.uniform.ppf(0.0), stats.uniform.ppf(1.0), 100)
        pyplot.plot(x, stats.uniform.pdf(x), color='black', lw=8, alpha=0.4)
        pyplot.xlabel('p (parameter of interest)')
        pyplot.ylabel('frequency')
        gray_line = lines.Line2D([], [], color='black', marker='_',
                                 markersize=10, label='prior', alpha=0.5)
        pyplot.legend(handles=[gray_line])
        pyplot.title('Posterior distribution of p', fontsize=14, y=1)
        return figure

    def post_summary(self):
        ''' Returns dictionary of statistics summarizing the posterior,
            estimates of p and inference of mu.'''
        posterior = numpy.array(self.posterior['parameter'])
        post_mean, post_median = posterior.mean(), numpy.median(posterior)
        post_norm = stats.norm(post_mean, posterior.std())
        alpha = 0.05
        l, u = post_norm.ppf(alpha / 2), post_norm.ppf((1 - alpha) / 2)
        mu = self.parent_N * post_median
        return {'p_mean': post_mean, 'p_median': post_median, 'p_CI': [l, u],
                'mu_estimate': mu, 'mu_CI': [l*self.parent_N, u*self.parent_N]}

    def tutorial(self, application='estimate'):
        ''' Coordinates display of appropriate figures with explanation of
            steps in ABC analysis.'''
        summary = self.post_summary()
        if application == 'estimate':
            print('1. Define true model\nWe start by defining a binomial distribution, that will represent our true\n model. We do not know the true model under normal circumstances that we use ABC\nto infer a parameter value, hence our great lengths to infer parameters. The\ntrue mean is mu = np = {}. Can we infer a good estimate?\nThis tutorial has true N set. We are attempting to infer p in order to estimate mu.\n'.format(self.parent_p*self.parent_N))
            pyplot.show(self.display_parent())
            print('\n2. Construct observed dataset\nWe sample n random variables from the true distribution to construct our\nobserved dataset. Under normal circumstances, this is the data we have collected\nand have in hand.\n')
            print('\n3. Calculate observed summary statistic\nWe calculate the summary statistic, {}, that attempts to\nsummarize our observed dataset in less complexity/dimensions and hold it in our\nback pocket for the rejection step.\n'.format(self.sumstat))
            print('\n4. Simulate datasets\nWe randomly draw estimates of p from a flat prior distribution\n[0, 1] and use it to construct an instance of our assumed model, the binomial\ndistribution. We construct a simulated dataset by sampling n random variables\nunder this fleeting model.\n')
            print('\n5. Calculate observed summary statistic\nWe calculate the summary statistic, {}, that attempts to summarize our\nsimulated dataset in less complexity/dimensions.\n'.format(self.sumstat))
            print('\n6. Rejection step\nWe calculate the distance between the observed and simulated summary\nstatistic, {}. We accept the estimate of p if this distance is below some\nthreshold (in this tutorial fixed at 1 standard deviation of the mean of the\nobserved data) and p is added to our posterior distribution. If the distance\nexceeds the threshold we throw out p.\n'.format(self.sumstat))
            pyplot.show(self.display_sumstats())
            print('\n7. Generate posterior distribution\nRepeats steps 4-6 iteratively until our posterior distribution includes\n{} estimates of p.\n'.format(self.posterior_size))
            pyplot.show(self.display_posterior())
            print('\n8. Summarize posterior\nWe infer p by summarizing the posterior distribution of p. We calculate the\nmedian of the posterior and the 95% credibility interval surrounding it. We\nestimate mu from our inferred median p = {}:\n'.format(round(summary['p_median'], 2)))
            print('TRUE mu = {} and ESTIMATED mu = {}'.format((self.parent_N*self.parent_p), round(summary['mu_estimate'], 2)))
        if application == 'select':
            pass
