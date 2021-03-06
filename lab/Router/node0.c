#include <stdio.h>
#include <string.h>

int isNeighbor0(int);
int sendToNeighbors0(int, int[]);

struct rtpkt {
    int sourceid;   /* id of sending router sending this pkt */
    int destid;     /* id of router to which pkt being sent
                       (must be an immediate neighbor) */
    int mincost[4]; /* min cost to node 0 ... 3 */
} rtpkt;

extern int TRACE;
extern int YES;
extern int NO;
extern float clocktime;

struct distance_table {
    int costs[4][4];
} dt0;

int minCost0[4];
int linkCost0[4];
int sendDV0;
/* students to write the following two routines, and maybe some others */

#define INFINITY 999
#define NODE0 0
#define TRUE 1
#define FALSE 0
void printdt0();
void rtinit0() {
    // 根据拓扑结构图进行初始化操作
    linkCost0[0] = 0;
    linkCost0[1] = 1;
    linkCost0[2] = 3;
    linkCost0[3] = 7;

    memcpy(dt0.costs[NODE0], linkCost0, sizeof(int[4]));
    memcpy(minCost0, linkCost0, sizeof(int[4]));
    sendDV0 = FALSE;

    printdt0();
    sendToNeighbors0(NODE0, minCost0);  // 发送给相邻的路由器
}

void rtupdate0(struct rtpkt *rcvdpkt) {
    //对路由表更新
    if (isNeighbor0(rcvdpkt->sourceid)) {
        int i;
        for (i = 0; i < 4; i++) {
            if (minCost0[i] > rcvdpkt->mincost[i]) {
                int possibleRoute =
                    minCost0[rcvdpkt->sourceid] + rcvdpkt->mincost[i];
                if (possibleRoute < minCost0[i]) {
                    minCost0[i] = possibleRoute;
                    sendDV0 = TRUE;
                }
            }
        }
        memcpy(dt0.costs[NODE0], minCost0, sizeof(int[4]));
        memcpy(dt0.costs[rcvdpkt->sourceid], rcvdpkt->mincost, sizeof(int[4]));
        printdt0();
    }
    if (sendDV0) {
        sendToNeighbors0(NODE0, minCost0);
        sendDV0 = FALSE;
    }
}

int isNeighbor0(int sourceid) { return linkCost0[sourceid] != INFINITY; }
int sendToNeighbors0(int sourceid, int mincost[]) {
    int i;
    for (i = 0; i < 4; i++) {
        if (isNeighbor0(i) && i != sourceid) sendrtpkt(sourceid, i, mincost);
    }
}
void printdt0() {
    printf("               via     \n");
    printf("   D0 |    0      1     2    3 \n");
    printf("  ----|------------------------\n");
    printf("     0|  %3d    %3d   %3d  %3d\n", dt0.costs[0][0], dt0.costs[0][1],
           dt0.costs[0][2], dt0.costs[0][3]);
    printf("     1|  %3d    %3d   %3d  %3d\n", dt0.costs[1][0], dt0.costs[1][1],
           dt0.costs[1][2], dt0.costs[1][3]);
    printf("dest 2|  %3d    %3d   %3d  %3d\n", dt0.costs[2][0], dt0.costs[2][1],
           dt0.costs[2][2], dt0.costs[2][3]);
    printf("     3|  %3d    %3d   %3d  %3d\n", dt0.costs[3][0], dt0.costs[3][1],
           dt0.costs[3][2], dt0.costs[3][3]);
}

void linkhandler0(int linkid, int newcost) {}
