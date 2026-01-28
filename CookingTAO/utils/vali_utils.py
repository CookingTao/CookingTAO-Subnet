from CookingTAO.utils.chain import get_chain_data
from CookingTAO.utils.api import get_subnet_miner

# filter hotkeys not in our whitelist
def rankings(self, netuids: list):
    """
    Filter hotkeys based on adopters from subnet miners.
    
    Arguments:
        self (Validator): Validator instance
        netuids (list): List of subnet netuids
    
    Returns:
        dict: A dictionary with subnet netuids as keys and their corresponding
              filtered rankings (list of tuples) as values.
    """
    
    chain_data = get_chain_data(netuids, self.subtensor)
    subnet_miners = get_subnet_miner(self.api_url)
    
    # Access adopters' hotkeys by netuid and map to their miner
    adopters_by_netuid = {}
    
    for netuid in netuids:
        if netuid in subnet_miners:
            # Create mapping of adopter hotkey to miner hotkey
            adopter_to_miner = {}
            netuid_miners = subnet_miners[netuid]
            for miner_hk, adopter_list in netuid_miners.items():
                for adopter_hk in adopter_list:
                    adopter_to_miner[adopter_hk] = miner_hk
            adopters_by_netuid[netuid] = adopter_to_miner
    # Filter chain data hotkeys based on adopters and include miner hotkey
    filtered_rankings = {}
    
    for netuid, rankings in chain_data.items():
        adopter_to_miner = adopters_by_netuid.get(str(netuid), {})
        
        # First, add ranking based on position in array
        # If incentive is 0, assign rank 255
        ranked_data = []
        for idx, (ck, hk, inc) in enumerate(rankings):
            rank = 255 if inc == 0 else idx 
            ranked_data.append((ck, hk, inc, rank))
        
        # Then filter based on adopters
        filtered_rankings[netuid] = [
            (adopter_to_miner[hk], ck, hk, inc, rank)
            for ck, hk, inc, rank in ranked_data
            if hk in adopter_to_miner
        ]
        
    return filtered_rankings