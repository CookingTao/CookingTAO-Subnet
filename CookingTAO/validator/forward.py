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

import time
import bittensor as bt

from CookingTAO.utils.uids import get_all_uids
from CookingTAO.utils.misc import ttl_get_block
from CookingTAO.validator.reward import get_rewards

def sleep_time(self) -> int:
    """Calculate the time to sleep for the next validation step."""
    current_block = ttl_get_block(self)
    cycle_length = self.config.neuron.epoch_length
    
    next_cycle_block = ((current_block // cycle_length) + 1) * cycle_length
    blocks_to_wait = next_cycle_block - current_block
    
    bt.logging.debug(f"Sleeping for {blocks_to_wait} blocks to wait for the next validation step.")
    return blocks_to_wait * 12

async def forward(self):
    """
    Main validation loop called every step.

    This function:
    1. Retrieves all miner UIDs
    2. Calculates rewards based on miner code performance across subnets
    3. Updates miner scores
    4. Sets network weights
    5. Saves validator state
    6. Waits for next step

    Args:
        self: The validator neuron instance containing configuration and state.
    """
    miner_uids = get_all_uids(self)

    rewards = get_rewards(self)

    bt.logging.info(f"Rewards: {rewards}")
    # Update the scores based on the rewards.
    self.update_scores(rewards, miner_uids)
    
    time.sleep(sleep_time(self))
