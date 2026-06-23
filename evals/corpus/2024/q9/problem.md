# AoC 2024 Day 9: Disk Fragmenter

The input is a single line "dense disk map" of digits where digits alternate between file lengths and free-space lengths; each file receives an incrementing ID (0, 1, 2, ...).

**Part 1:** Compact the disk by moving file blocks one at a time from the rightmost filled block into the leftmost free block until no gaps remain, then compute the checksum as the sum of (block position x file ID) over all filled blocks.

**Part 2:** Instead, move each whole file exactly once (highest file ID first) into the leftmost span of free space large enough to hold it, then recompute the checksum the same way.
