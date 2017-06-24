# -*- coding: utf-8 -*-
""" ===========================================================================

This script is where we implement the dynamical rules governing the
interaction between nodes and the evolution of the network

NOTE: Right now, if a node has positive liquidity it will prioritize investing
in neighbors with the least amount of negative liquidity for the following
reasons: this bank is the easiest to balance out, and thus it is the
safest bet for the bank with positive liquidity. For this bank it's most
likely that it won't lose its investment.

Also, if it has several debts, it will repay the large debts back first,
where the rationale is that large debts would have large interest payments,
so there's more incentive to repay those

NOTE FOR UNDERSTANDING SYNTAX:
nodes look like this: 
    (name, {'capital': 0, 'liquidity': 0, 'bankrupt': False})
edges like this: 
    (name1, name2, {'debt': 0, 'lender': None, 'borrower': None})
    
For a given node n and edge e, n[0] gives its name and n[1] gives
the associated dictionary with extra attributes. e[0] and e[1] give the names
of the associated nodes, while e[2] gives the dictionary with extra attributes.
It should also be noted that these names DON'T have to be strings. In fact,
for the lattice/regular network they're tuples of integers, eg (0,1)

NOTE: I think this could be a difference between my implementation and the
article: when infected nodes lose capital due to a neighboring node failing,
they proceed to recover ALL loaned money. I felt like this is what the 
article implied in the rule section, in the 5th bullet point. However,
I could imagine they only recover the amount of loaned money they lost, 
which would reduce the amount of avalanches I think. Maybe that's how they 
implemented it?

=========================================================================== """

import random

''' Run the simulation for T iterations '''
def run_simulation(network, T):
    avalanche_sizes = []  # list of the sizes of all avalanches
    
    # Simulation kernel
    for t in range(T):
        # Generate random perturbations in the liquidity for each node
        _perturb(network)
        
        # Banks with surplus liquidity try to repay debts
        _repay_debts(network)

        # Banks without surplus can collect money back
        _collect_loans(network)
        
        # Banks with surplus liquidity try to invest in neighbors with negative liquidity
        _invest_surplus_liquidity(network)
        
        DEBUG_FUNCTION(network, t)
        
        # Check for bankruptcy and propagate infection/failures. If an avalanche happens, its size is appended to avalanche_sizes
        _check_and_propagate_avalanche(network, avalanche_sizes, t)
                    
    # Return the list of avalanche sizes
    return avalanche_sizes

''' Each bank gets or loses some capital randomly (delta=1 v delta=-1) '''
def _perturb(network):
    for node in network.nodes():  # data=True makes it retrieve all extra attributes
        # Randomly generate delta    
        delta = random.choice([-1, 1])
        # Update liquidity and capital
        node.changeLiquidity(delta)
        node.changeCapital(delta)

''' Banks with surplus liquidity repay debts  '''
def _repay_debts(network):
    # Iterate through the node list randomly
    node_list = network.nodes()[:]
    random.shuffle(node_list)
    _pay_money(node_list)


''' Banks with negative liquidity collect loans  '''
def _collect_loans(network):
    # Iterate through the node list randomly
    node_list = network.nodes()[:]
    random.shuffle(node_list)
    _get_money(node_list)


''' Banks with surplus liquidity try to invest in neighbors with negative liquidity '''
def _invest_surplus_liquidity(network):
    # Iterate through the node list randomly
    node_list = network.nodes()[:]
    random.shuffle(node_list)
    for node in node_list:        
        # If there's still liquidity left, help out any broke neighbors
        if node.getLiquidity() > 0:
            node.findBrokeNeighbours()
            broke_neighbours = node.getBrokeNeighbours()
            # Iterate through broke neighbors to invest in
            for broke in broke_neighbours:
                money_needed = -broke.getLiquidity()  # How much money does this neighbor need?
                if node.getLiquidity() >= money_needed:  # Do I have enough money for that?
                    node.transfer(broke, money_needed)  # Transfer that amount
                else:
                    node.transfer(broke, node.getLiquidity())  # Else transfer what I have
                    break
    
''' Check for bankrupty and spread infections. Note, I'm calling it 
    avalanche now to distinguish between:
    - avalanche: cascade of failures
    - infection: cascade of banks trying to regain balance by asking money from borrowers '''
def _check_and_propagate_avalanche(network, avalanche_sizes, t):
    # If any bank has gone bankrupt, start an infection. Also get a list of bankrupt banks
    bankrupt_banks = _find_bankruptcies(network, t)  # list of bankrupt banks is a list of names
#    DEBUG_FUNCTION(network, t)
    if len(bankrupt_banks) > 0:  # If there are bankrupt banks
        _infect_neighbours(bankrupt_banks)  # Sets lender neighbours of bankrupt banks to infected
        infected_banks = _find_infections(network) # Puts for infected banks in a list
        length_old_infections = len(infected_banks) 
        if len(infected_banks) > 0:  # When there are infections
              while True:
                _spread_infections(infected_banks)  # Infected nodes repay/pay to neighbors and infect them
                bankrupt_banks = _find_bankruptcies(network, t)  # Find any new bankruptcies
                _infect_neighbours(bankrupt_banks)  # Make neighbors of new bankruptcies also infected
                infected_banks = _find_infections(network)  # Finds those infections 
                length_new_infections = len(infected_banks)
                if length_new_infections == length_old_infections:  # When there are no new infection, we stop the avalanche
                    avalanche_sizes.append(length_new_infections)
                    _cure(infected_banks)  # Cures infected banks
                    _reset(bankrupt_banks)  #resets every bank
                    break
                else:
                    length_old_infections = length_new_infections
        else:
            _reset(bankrupt_banks)
 
''' =========================================================================== 
HELPER FUNCTIONS
=========================================================================== '''

def DEBUG_FUNCTION(network, t):
    for node in network.nodes():
        # if a node is a borrower and a lender, raise an exception
        borrowing, lending = False, False
        for neighbour in node.neighbours:
            if node.neighbours[neighbour] > 0:
                lending = True
            elif node.neighbours[neighbour] < 0:
                borrowing = True
        if borrowing and lending:
            Exception("A node is borrowing and lending at the same time in iteration %i. This shouldn't happen!" % t)

def DEBUG_FUNCTION_SINGLE_NODE(node, t):
    # if a node is a borrower and a lender, raise an exception
    borrowing, lending = False, False
    for neighbour in node.neighbours:
        if node.neighbours[neighbour] > 0:
            lending = True
        elif node.neighbours[neighbour] < 0:
            borrowing = True
    if borrowing and lending:
        Exception("A node is borrowing and lending at the same time in iteration %i. This shouldn't happen!" % t)

''' Helper function for checking if any banks are now bankrupt '''           
def _find_bankruptcies(network, t):
    bankrupt_banks = []
    for node in network.nodes():
        DEBUG_FUNCTION_SINGLE_NODE(node, t)
        # Check whether this node is bankrupt
        if node.getCapital() <= network.graph['Ts'] or node.getLiquidity() <= network.graph['Tl']:
            node.setBankruptcy(True)
            bankrupt_banks.append(node)
            
    return bankrupt_banks

'''Helper function for creating infections'''
def _infect_neighbours(bankrupt_banks):
    for bank in bankrupt_banks:
        bank.findBorrowersLenders()
        lenders = bank.getLenders()
        for lender in lenders:
            lender.infect(bank)

'''Helper function to find infections'''
def _find_infections(network):
    infected_banks = []
    for bank in network.nodes():
        if bank.getInfection():
            infected_banks.append(bank)
    return infected_banks

'''Helper function to cure infections'''
def _spread_infections(infected_banks):
    _get_money(infected_banks, cure = 1)
    _pay_money(infected_banks, cure = 1)

''' Helper function to get money '''
def _get_money(node_list, cure = 0):
    for node in node_list:
        # Do I have money?
        if node.getLiquidity() < 0 or cure:
            # Determine if this node is in debt, and to whom
            node.findBorrowersLenders()
            borrowers = node.getBorrowers()  # List of neighbours who are borrowers
            # Repay as much as possible to the lender associated with the highest current debt
            for borrower in borrowers:
                debt = node.getDebt(borrower) # How much money do I get?
                if abs(node.getLiquidity()) >= debt or cure:  # Is it enough?
                    node.transfer(borrower, -debt) # Take that amount which is present
                    if cure:
                        borrower.infect()
                else:
                    node.transfer(borrower, node.getLiquidity()) # Take whatever is needed, surplus covered.
                    if cure:
                        borrower.infect()
#                            node.cure()
                    break

'''Helper function to pay money'''
def _pay_money(node_list, cure=0):
    for node in node_list:
        # Do I have money?
        if node.getLiquidity() > 0 or cure:
            # Determine if this node is in debt, and to whom
            node.findBorrowersLenders()
            lenders = node.getLenders()  # lenders is a dict with names as keys and loansizes as values
            if len(lenders) > 0:
                # Repay as much as possible to the lender associated with the highest current debt
                
                for lender in lenders:
                    debt = node.getDebt(lender) # How much money do I owe?
                    if node.getLiquidity() >= debt or cure:  # Do I have enough money to payback?
                        node.transfer(lender, debt) # Payback that amount
                        if cure:
                            lender.infect()
                    else:
                        node.transfer(lender, node.getLiquidity()) # If I can't payback the whole pay, pay how much I have?
                        if cure:
                            lender.infect()
                        break
                    
'''Helper function to cure Banks'''
def _cure(banks):
    for bank in banks:
        bank.cure()

''' Helper function for resetting banks '''
def _reset(banks):
    for bank in banks:
        bank.reset()
