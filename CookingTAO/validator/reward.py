# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2026 Epic Tensor

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
import numpy as np
import bittensor as bt
from CookingTAO.utils.vali_utils import rankings
from CookingTAO.utils.api import get_PE, get_subnets


def reward(self) -> float:
    """
    Calculates raw weights for miners based on their adoption across subnets.
    
    This method computes pair weights by combining:
    - Rank score: Position of miner in subnet (higher rank = better score)
    - Incentive score: Proportion of total incentives earned
    - Importance factor: Subnet-specific importance multiplier
    - Adoption bonus: Reward for being adopted by users (0.1 weight)
    
    Returns:
    - dict: Mapping of miner hotkeys to their raw weight values
    """
    bt.logging.info("Calculating raw weights:")

    imp_factor = get_subnets(self.api_url)
    ranking = rankings(self, netuids=list(imp_factor.keys()))
    total_adopters = sum(len(ranked_list) for ranked_list in ranking.values())
    
    adoption = 1 / total_adopters if total_adopters > 0 else 0.0
    total_incentives = sum(incentive for ranked_list in ranking.values() for _, _, _, incentive, _ in ranked_list)
    raw_weights = {}
    
    for netuid, ranked_list in ranking.items():
        importance = float(imp_factor.get(str(netuid), 0.0))
        
        for miner_hk, _, _, incentive, rank in ranked_list:
            if total_incentives > 0:
                rank_score = (255 - rank) / 255
                incentive_score = incentive / total_incentives
                pair_weight = (rank_score * incentive_score) * importance * 0.9 + adoption * 0.1
            else:
                pair_weight = 0.0
                
            raw_weights[miner_hk] = raw_weights.get(miner_hk, 0.0) + pair_weight
            
            bt.logging.info(
                f"{netuid} {pair_weight:.10f} {importance:.10f} {adoption:.10f}"
            )
            
    bt.logging.info(f"Raw rewards: {raw_weights}")
    return raw_weights


def get_rewards(
    self
) -> np.ndarray:
    """
    Calculates and returns normalized reward array for all miners based on their performance.
    
    The function:
    1. Retrieves raw weights from the reward() function
    2. Compares Platform Earnings (PE) vs Subnet Earnings (SE)
    3. Applies miner proportion scaling if SE > PE
    4. Caps individual rewards at 0.3
    5. Burns any remainder to owner uid
    
    Returns:
    - np.ndarray: Normalized array of rewards
    """
    
    rewards = reward(self)
    hotkeys = self.hotkeys
    PE = get_PE(self.api_url) # Platform Earning in next epoch
    # alpha_price = float(self.subtensor.get_subnet_price(netuid=self.config.neuron.netuid)) * 10000 # Current alpha price
    alpha_price = 0.01 # Fixed alpha price for CookingTAO
    SE = 148.01 * alpha_price # Miners receives 148.01 alpha per epoch
    
    if PE <= 0: # No users in CookingTAO
        rewards_array = np.array([0.0 for _ in hotkeys])
        rewards_array[0] = 1.0  # Burn all rewards
        return rewards_array
    
    rewards_array = np.array([rewards.get(hk, 0.0) for hk in hotkeys])
    total_reward = np.sum(rewards_array)
    
    if total_reward <= 0:
        rewards_array = np.array([0.0 for _ in hotkeys])
        rewards_array[0] = 1.0  # Burn all rewards
        return rewards_array
    
    rewards_array /= total_reward # Normalize to sum of 1
    
    if SE > PE:
        rewards_array *= (PE / SE) # Rewards array x Miner Proportion
    
    rewards_array = np.minimum(rewards_array, 0.3) # Cap individual max reward to 0.3
    rewards_array[0] = 1.0 - np.sum(rewards_array) # Burn remainder
    
    bt.logging.info("Final Rewards:", rewards_array )
    return rewards_array
    