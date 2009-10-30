// (c) 2009 Peter Todd

// ROM is reasonably plentiful, RAM is not.

// The actual tables should leave the first entry's unused, so !some_node_idx
// will behave the same if node indexes are later converted to pointers.
typedef uint16_t node_idx;
typedef uint16_t vertex_idx;

typedef struct {
    unsigned int idx : 8;
    unsigned int end : 1;
} edge_idx;


// Goals. Using just two goals right now, simple and clean, and good for a horizontal presentaiton.
#define NUM_GOALS 2
typedef enum {
    Light = 0,
    Dark = 1
} goal_t;

// The pathfinding functions as a sort of bastardized Dijkstra's, where each
// ant is performing the distance finding.
typedef uint16_t goal_dist_t;

struct ant {
    uint16_t cur_edge_i;
    edge_idx cur_edge;
    vertex_idx cur_vertex;

    // Current goal and how far away we are from it.
    goal_t goal;
    goal_dist_t goal_dist;
};



// An individual led that an ant may be on. Only one ant may be present on a
// node at any time.
//
// The nodes really refers to which led we want to light up, so "x" and "y"
// could be something like chip select and index, especially given that 256 led
// controllers are available.
//
// All this can be stored in ROM.
#define NUM_NODES 2048
struct node_rom {
    uint8_t x;
    uint8_t y;
};

struct node_ram {
    struct ant *ant;
};

// A vertex is a node that connects edges together.
//
// Vertexes are where decisions about which direction to go are made.
#define NUM_VERTEX_EDGES 4
struct vertex_rom {
    node_idx node;

    edge_idx edges[NUM_VERTEX_EDGES];
};

// An edge is a list of nodes connecting vertexes.
//
// Importantly, an edge has the idea of both how many ants are present along
// it, and a direction of travel.
//
// Edges are also goal locations, generalizing the idea of nodes being goals.
// Since an ant on an edge will travel every node on the edge (ignoring changes
// in direction) the edge itself can be the goal.
#define MAX_VERTEX_NEIGHBORS (4)
struct edge_rom {
    uint8_t num_nodes;
    uint16_t nodes[];
};

struct edge_ram {
    int8_t travel_direction;
    uint8_t ants_present;

    // Goal distances by goal type for each end of the edge.
    goal_dist_t goal_dists[2][NUM_GOALS];
};
