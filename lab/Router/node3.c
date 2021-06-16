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

struct distance_table {
    int costs[4][4];
} dt3;

void printdt3(struct distance_table *dtptr);
/* students to write the following two routines, and maybe some others */
int direct_distance3[4];

void send_to_neighbour3() {
    struct rtpkt pkt;
    pkt.mincost[0] = dt3.costs[0][3];
    pkt.mincost[1] = dt3.costs[1][3];
    pkt.mincost[2] = dt3.costs[2][3];
    pkt.mincost[3] = dt3.costs[3][3];

    pkt.sourceid = 3;
    pkt.destid = 0;
    tolayer2(pkt);

    pkt.destid = 2;
    tolayer2(pkt);
}

int update3() {
    int flag = 0;
    int min_dis;
    for (int i = 0; i < 3; i++) {
        min_dis = min(direct_distance3[0] + dt3.costs[i][0],
                      direct_distance3[2] + dt3.costs[i][2]);
        if (min_dis != dt3.costs[i][3]) {
            dt3.costs[i][3] = min_dis;
            flag = 1;
        }
    }
    return flag;
}

void rtinit3() {
    // 根据拓扑结构图进行初始化操作
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            if (i == j)
                dt3.costs[i][j] = 0;
            else
                dt3.costs[i][j] = 16;
        }
    }
    direct_distance3[0] = dt3.costs[0][3] = 7;
    direct_distance3[1] = dt3.costs[1][3] = 16;
    direct_distance3[2] = dt3.costs[2][3] = 2;
    direct_distance3[3] = dt3.costs[3][3] = 0;
    send_to_neighbour3();  // 发送给相邻的路由器
}

void rtupdate3(struct rtpkt *rcvdpkt) {
    //对路由表更新
    for (int i = 0; i < 4; i++)
        dt3.costs[i][rcvdpkt->sourceid] = rcvdpkt->mincost[i];

    if (update3())
        send_to_neighbour3();
    else {
        // printdt3(&dt3);
        //打印出路由表
        printf("node3 distance_table: ");
        for (int i = 0; i < 4; i++) {
            printf("%d ", dt3.costs[i][3]);
        }
        printf("\n");
    }
}

void printdt3(struct distance_table *dtptr) {
    printf("             via     \n");
    printf("   D3 |    0     2 \n");
    printf("  ----|-----------\n");
    printf("     0|  %3d   %3d\n", dtptr->costs[0][0], dtptr->costs[0][2]);
    printf("dest 1|  %3d   %3d\n", dtptr->costs[1][0], dtptr->costs[1][2]);
    printf("     2|  %3d   %3d\n", dtptr->costs[2][0], dtptr->costs[2][2]);
}
