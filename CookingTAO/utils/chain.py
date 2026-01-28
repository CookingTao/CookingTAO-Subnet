"""
Chain utility functions
"""

def get_chain_data(
    whitelisted_subnets: list,
    subtensor: "bt.Subtensor",
    ):
    """
    Fetch chain data for whitelisted subnets.

    Arguments:
        whitelisted_subnets (list): Whitelisted subnet netuids list
        subtensor (bt.Subtensor): Subtensor API instance
    
    Returns:
        dict: A dictionary with subnet netuids as keys and their corresponding
              rankings (list of tuples) as values.
    """
    try:
        data = subtensor.get_all_metagraphs_info()

        rankings = {}

        for netuid in whitelisted_subnets:
            try:
                netuid = int(netuid)
                subnet = data[netuid]

                coldkeys = subnet.coldkeys
                hotkeys = subnet.hotkeys
                incentive = subnet.incentives

                rank = sorted(zip(coldkeys, hotkeys, incentive), key=lambda x: x[2], reverse=True)

                rankings[netuid] = rank

            except Exception as e:
                print(f"Error processing netuid {netuid}: {e}")
                rankings[netuid] = []
                
    except Exception as e:
        print(f"Error fetching metagraphs info: {e}")
        rankings = {}
        
    return rankings