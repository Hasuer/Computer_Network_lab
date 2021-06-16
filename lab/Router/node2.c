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
} dt2;

void printdt2(struct distance_table *dtptr);
/* students to write the following two routines, and maybe some others */
int direct_distance2[4];

void send_to_neighbour2() {
    struct rtpkt pkt;
    pkt.mincost[0] = dt2.costs[0][2];
    pkt.mincost[1] = dt2.costs[1][2];
    pkt.mincost[2] = dt2.costs[2][2];
    pkt.mincost[3] = dt2.costs[3][2];

    pkt.sourceid = 2;
    pkt.destid = 0;
    tolayer2(pkt);

    pkt.destid = 1;
    tolayer2(pkt);

    pkt.destid = 3;
    tolayer2(pkt);
}

int update2() {
    int flag = 0;
    int min_dis;
    for (int i = 0; i < 4; i++) {
        if (i == 2) continue;
        min_dis = min(direct_distance2[0] + dt2.costs[i][0],
                      min(direct_distance2[1] + dt2.costs[i][1],
                          direct_distance2[3] + dt2.costs[i][3]));
        if (min_dis != dt2.costs[i][2]) {
            dt2.costs[i][2] = min_dis;
            flag = 1;
        }
    }
    return flag;
}

void rtinit2() {
    // 根据拓扑结构图进行初始化操作
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            if (i == j)
                dt2.costs[i][j] = 0;
            else
                dt2.costs[i][j] = 999;
        }
    }
    direct_distance2[0] = dt2.costs[0][2] = 3;
    direct_distance2[1] = dt2.costs[1][2] = 1;
    direct_distance2[2] = dt2.costs[2][2] = 0;
    direct_distance2[3] = dt2.costs[3][2] = 2;
    send_to_neighbour2(); // 发送给相邻的路由器
}

void rtupdate2(struct rtpkt *rcvdpkt) {
    // 对路由表更新
    {
        for (int i = 0; i < 4; i++)
            dt2.costs[i][rcvdpkt->sourceid] = rcvdpkt->mincost[i];

        if (update2())
            send_to_neighbour2();
        else {
            // printdt2(&dt2);
            //打印路由表
            printf("node2 distance_table: ");
            for (int i = 0; i < 4; i++) {
                printf("%d ", dt2.costs[i][2]);
            }
            printf("\n");
        }
    }
}

void printdt2(struct distance_table *dtptr){
    printf("                via     \n");
    printf("   D2 |    0     1    3 \n");
    printf("  ----|-----------------\n");
    printf("     0|  %3d   %3d   %3d\n", dtptr->costs[0][0], dtptr->costs[0][1],
           dtptr->costs[0][3]);
    printf("dest 1|  %3d   %3d   %3d\n", dtptr->costs[1][0], dtptr->costs[1][1],
           dtptr->costs[1][3]);
    printf("     3|  %3d   %3d   %3d\n", dtptr->costs[3][0], dtptr->costs[3][1],
           dtptr->costs[3][3]);
}
