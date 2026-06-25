from main import read_input

class Region:
    def __init__(self, region_id, crop, plots):
        self.region_id = region_id
        self.crop = crop
        self.plots = plots
        self.perimeter = self.derive_perimeter()
        self.num_sides = self.derive_num_sides()

    def __str__(self):
        return f"{self.crop} (id={self.region_id}). #plots={len(self.plots)}. #perimeter={len(self.perimeter)}. #sides={self.num_sides}. plots: {self.plots}"

    def derive_perimeter(self):
        # Step 1: Generate all directional boundaries for each plot.
        # Of form (x, y, vertical/horizontal, north/east/south/west)
        boundaries_nested = [[(x,y,'v','w'), (x+1,y,'v','e'), (x,y,'h','n'), (x,y+1,'h','s')] for (x, y) in self.plots]
        all_boundaries = [x for boundaries in boundaries_nested for x in boundaries]

        # Step 2: Count occurrences of directionless boundaries (just by position + orientation)
        boundary_counts = {}
        for x, y, orientation, _ in all_boundaries:
            boundary_key = (x, y, orientation)
            boundary_counts[boundary_key] = boundary_counts.get(boundary_key, 0) + 1

        # Step 3: Extract boundaries that only appear once — i.e. perimeter edges.
        perimeter_keys = {key for key, count in boundary_counts.items() if count == 1}

        # Step 4: Filter original boundaries to only include those on the perimeter.
        fences = [(x, y, vh, nesw) for (x, y, vh, nesw) in all_boundaries if (x, y, vh) in perimeter_keys]
        return fences

    def derive_num_sides(self):
        """
        Calculates the number of distinct sides in the perimeter by checking for
        connected boundaries with matching orientation and direction.
        """
        def is_touching(f1, f2):
            x1, y1, orientation1, direction1 = f1
            x2, y2, orientation2, direction2 = f2

            if direction1 != direction2 or orientation1 != orientation2:
                return False

            if orientation1 == 'h':
                return abs(x1 - x2) == 1 and y1 == y2
            if orientation1 == 'v':
                return abs(y1 - y2) == 1 and x1 == x2

            return False

        # Separate and sort fences for orderly comparison.
        verticals = sorted(
            [f for f in self.perimeter if f[2] == 'v'],
            key=lambda f: (f[3], f[0], f[1])  # direction, x, y
        )
        horizontals = sorted(
            [f for f in self.perimeter if f[2] == 'h'],
            key=lambda f: (f[3], f[1], f[0])  # direction, y, x
        )

        sides = 0
        seen = set()
        for fence in verticals + horizontals:
            if not any(is_touching(fence, seen_fence) for seen_fence in seen):
                sides += 1
            seen.add(fence)

        return sides

def fence_price(region):
    # Price := #plots * perimeter
    return len(region.plots) * len(region.perimeter)

def fence_price_bulk_discount(region):
    # Price := #plots * #sides
    return len(region.plots) * region.num_sides

def touching(x, y, x1, y1):
    return (x==x1 and abs(y-y1) <= 1) or (y==y1 and abs(x-x1)  <= 1)

def plot_exists(raw, x, y):
    return 0 <= y < len(raw) and 0 <= x < len(raw[y])

def adjacent_plots(raw, x, y):
    adjacent = []
    if plot_exists(raw, x, y-1):
        adjacent.append((x, y-1, raw[y-1][x]))
    if plot_exists(raw, x, y+1):
        adjacent.append((x, y+1, raw[y+1][x]))
    if plot_exists(raw, x-1, y):
        adjacent.append((x-1, y, raw[y][x-1]))
    if plot_exists(raw, x+1, y):
        adjacent.append((x+1, y, raw[y][x+1]))
    return adjacent

def derive_regions(raw):
    next_region_id = 0
    regions = {} # { (region_id, crop): [(x1, y1), ... (x_n, y_n)] }
    # Search plots dfs by region to avoid orphaned regions.
    plots_to_visit = []
    # Generate initial list of all plots to be visited.
    for y in range(len(raw)):
        for x in range(len(raw[y])):
            crop = raw[y][x]
            plots_to_visit.append((x, y, crop)) # Just for debugging

    visited = set()
    while len(plots_to_visit) > 0:
        plot = plots_to_visit.pop()
        if plot in visited:
            continue

        joined_existing_region = False
        (x, y, crop) = plot

        # See if plot can join any existing region.
        for (region_id, existing_crop), plots in regions.items():
            if joined_existing_region:
                break
            if not crop == existing_crop:
                continue
            for p in plots:
                (x1, y1) = p
                if touching(x, y, x1, y1):
                    regions[(region_id, existing_crop)].append((x, y))
                    joined_existing_region = True
                    break
        if not joined_existing_region:
            regions[(next_region_id, crop)] = [(x, y)]
            next_region_id += 1

        # DFS for neighbouring plots with same crop.
        for adjacent in adjacent_plots(raw, x, y):
            (x_adj, y_adj, crop_adj) = adjacent
            if crop_adj == crop and not adjacent in visited:
                plots_to_visit.append(adjacent)

        visited.add(plot)

    # Construct {id: Region()} from intermediary structure.
    return { region_id: Region(region_id, crop, plots) for (region_id, crop), plots in regions.items()}

def part1() -> int:
    regions = derive_regions(read_input('q12.txt'))
    return sum([fence_price(region) for region in regions.values()])

def part2() -> int:
    regions = derive_regions(read_input('q12.txt'))
    return sum([fence_price_bulk_discount(region) for region in regions.values()])

print(part1())
print(part2())