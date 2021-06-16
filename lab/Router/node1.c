#include <stdio.h>
#include <stdlib.h>
#define min(a, b) (a > b ? b : a)

struct rtpkt {
    int sourceid;   /* id of sending router sending this pkt */
    int destid;     /* id of router to which pkt being sent
                           (must be an immediate neighbor) */
    int mincost[4]; /* min cost to node 0 ... 3 */
};

extern int TRACE;
extern int YES;
extern int NO;
extern void tolayer2(struct rtpkt packet);

int connectcosts1[4] = {1, 0, 1, 999};

struct distance_table {
    int costs[4][4];
} dt1;

void printdt1(struct distance_table *dtptr);
/* students to write the following two routines, and maybe some others */
int direct_distance1[4];

void send_to_neighbour1() {
    struct rtpkt pkt;
    pkt.mincost[0] = dt1.costs[0][1];
    pkt.mincost[1] = dt1.costs[1][1];
    pkt.mincost[2] = dt1.costs[2][1];
    pkt.mincost[3] = dt1.costs[3][1];

    pkt.sourceid = 1;
    pkt.destid = 0;
    tolayer2(pkt);

    pkt.destid = 2;
    tolayer2(pkt);
}

int update1() {
    int flag = 0;
    int min_dis;
    for (int i = 0; i < 4; i++) {
        if (i == 1) continue;
        min_dis = min(direct_distance1[0] + dt1.costs[i][0],
                      direct_distance1[2] + dt1.costs[i][2]);
        if (min_dis != dt1.costs[i][1]) {
            dt1.costs[i][1] = min_dis;
            flag = 1;
        }
    }
    return flag;
}

void rtinit1() {
    // 根据拓扑结构图进行初始化操作
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            if (i == j)
                dt1.costs[i][j] = 0;
            else
                dt1.costs[i][j] = 16;
        }
    }
    direct_distance1[0] = dt1.costs[0][1] = 1;
    direct_distance1[1] = dt1.costs[1][1] = 0;
    direct_distance1[2] = dt1.costs[2][1] = 1;
    direct_distance1[3] = dt1.costs[3][1] = 16;
    send_to_neighbour1();  // 发送给相邻的路由器
}

void rtupdate1(struct rtpkt *rcvdpkt) {
    // 对路由表更新
    for (int i = 0; i < 4; i++)
        dt1.costs[i][rcvdpkt->sourceid] = rcvdpkt->mincost[i];

    if (update1())
        send_to_neighbour1();
    else {
        // printdt1(&dt1);
        //打印路由表
        printf("node1 distance_table: ");
        for (int i = 0; i < 4; i++) {
            printf("%d ", dt1.costs[i][1]);
        }
        printf("\n");
    }
}

void printdt1(struct distance_table *dtptr) {
    printf("             via   \n");
    printf("   D1 |    0     2 \n");
    printf("  ----|-----------\n");
    printf("     0|  %3d   %3d\n", dtptr->costs[0][0], dtptr->costs[0][2]);
    printf("dest 2|  %3d   %3d\n", dtptr->costs[2][0], dtptr->costs[2][2]);
    printf("     3|  %3d   %3d\n", dtptr->costs[3][0], dtptr->costs[3][2]);
}

void linkhandler1(linkid, newcost) int linkid, newcost;
/* called when cost from 1 to linkid changes from current value to newcost*/
/* You can leave this routine empty if you're an undergrad. If you want */
/* to use this routine, you'll need to change the value of the LINKCHANGE */
/* constant definition in prog3.c from 0 to 1 */

{
    direct_distance1[linkid] = newcost;
    if (update1())
        send_to_neighbour1();
    else {
        // printdt1(&dt1);
        printf("node1 distance_table: ");
        for (int i = 0; i < 4; i++) {
            printf("%d ", dt1.costs[i][1]);
        }
        printf("\n");
    }
}
