# coding=utf-8
import numpy as np

import cfg


def should_merge(region, i, j):
    neighbor = set()
    for index in range(cfg.horizon_pixel_extend):
        neighbor.add((i, j-index-1))
        # neighbor.add((i, j+index))

    #neighbor = {(i, j - 1)}
    return not region.isdisjoint(neighbor)


def region_neighbor(region_set):
    """
    判断邻居的方法，相当于把当前的像素点行往下平移一个位置，然后头和尾巴均增加一个像素点
    :param region_set:
    :return:
    """
    # set转换成列表
    region_pixels = np.array(list(region_set))
    # 获得x轴最小的像素点坐标
    j_min = np.amin(region_pixels, axis=0)[1] - 1
    # 获得x轴最大的像素点坐标
    j_max = np.amax(region_pixels, axis=0)[1] + 1
    # 获得最小的m+1（这里因为每个像素点行都只有一个像素点高，因此max和min是一样的）
    i_m = np.amin(region_pixels, axis=0)[0] + 1
    # 所有的y坐标都+1，来模拟邻居
    region_pixels[:, 0] += 1
    # 列表转set
    neighbor = {(region_pixels[n, 0], region_pixels[n, 1]) for n in
                range(len(region_pixels))}
    # 添加头和尾巴两个坐标点
    neighbor.add((i_m, j_min))
    neighbor.add((i_m, j_max))

    return neighbor


def region_group(region_list):
    # 创建 像素点行 的索引列表
    S = [i for i in range(len(region_list))]
    # 存放 区域整合 后的列表
    D = []
    # 循环每个 像素点行
    while len(S) > 0:
        # 首先把当前的像素点行 移出列表
        m = S.pop(0)
        if len(S) == 0:
            # 如果像素点行是最后一个孤立的行，则直接加入到D列表中
            # S has only one element, put it to D
            D.append([m])
        else:
            # 基于当前像素点行，判断它和其他的所有的像素点行，是否是邻居
            D.append(rec_region_merge(region_list, m, S))
    return D


def rec_region_merge(region_list, m, S):
    """
    寻找该 像素点行m 的邻居
    :param region_list: 像素点行列表
    :param m:           查询的像素点行
    :param S:           判断是否为邻居的列表
    :return:
    """
    rows = [m]
    tmp = []
    for n in S:
        # 分别从m和n的角度判断，对方是否是自己的邻居
        if not region_neighbor(region_list[m]).isdisjoint(region_list[n]) or \
                not region_neighbor(region_list[n]).isdisjoint(region_list[m]):
            # 第m与n相交
            tmp.append(n)
    # 在S中移除所有的邻居点
    for d in tmp:
        S.remove(d)
    # 基于这些新的邻居点，判断是否有新的邻居
    # 最后都扩展到rows中
    for e in tmp:
        rows.extend(rec_region_merge(region_list, e, S))
    return rows


def nms(predict, activation_pixels, threshold=cfg.side_vertex_pixel_threshold):
    region_list = []
    # 这一阶段，可以把水平相邻的点放在一起。
    for i, j in zip(activation_pixels[0], activation_pixels[1]):
        merge = False
        for k in range(len(region_list)):
            # 观察是否能进行合并处理, 判断像素点{(x,y)}里面是否包含(x,y-1)
            if should_merge(region_list[k], i, j):
                # 给该点追加元素
                region_list[k].add((i, j))
                merge = True
                # Fixme 重叠文本区域处理，存在和多个区域邻接的pixels，先都merge试试
                # break
        if not merge:
            # 追加坐标点
            region_list.append({(i, j)})
    # 像素点行 之间的合并组合
    D = region_group(region_list)
    quad_list = np.zeros((len(D), 4, 2))
    score_list = np.zeros((len(D), 4))

    for group, g_th in zip(D, range(len(D))):
        total_score = np.zeros((4, 2))
        # 按照最左边的x进行排序，左上角的点仅依赖于第一个row进行预测；右下角的顶点依赖于最后一个row进行预测
        for row in group:
            for ij in region_list[row]:
                # score 为 是否为边界像素
                score = predict[ij[0], ij[1], 1]

                if score >= threshold:
                    # ith_score 为 是否为头
                    ith_score = predict[ij[0], ij[1], 2:3]
                    # 0.1 < ith_score < 0.9 TODO 不太理解这里的截取是在干嘛
                    if not (cfg.trunc_threshold <= ith_score < 1 - cfg.trunc_threshold):
                        # 四舍五入取整
                        # np.around([-0.5,0.5,1.5,2.5,3.5,4.5])
                        # [-0.  0.  2.  2.  4.  4.]
                        ith = int(np.around(ith_score))
                        # 如果小于等于0.5，则total_score为前两个元素加分
                        # 如果大于0.5，则total_score为后两个元素加分
                        total_score[ith * 2:(ith + 1) * 2] += score
                        # 针对像素分别进行x和y的扩大
                        px = (ij[1] + 0.5) * cfg.pixel_size
                        py = (ij[0] + 0.5) * cfg.pixel_size
                        # 针对后四个坐标进行平移
                        p_v = [px, py] + np.reshape(predict[ij[0], ij[1], 3:7], (2, 2))
                        # TODO 不理解score*p_v是什么意思
                        # TODO 暂时的理解是，每个点都会预测所在文本框的左上角的坐标和右下角的坐标
                        # TODO 然后通过各自的分值作为置信度，头预测左上，尾预测右下，最后计算一个平均值
                        quad_list[g_th, ith * 2:(ith + 1) * 2] += score * p_v

        # for row in group:
        #     for ij in region_list[row]:
        #         # score 为 是否为边界像素
        #         score = predict[ij[0], ij[1], 1]
        #
        #         if score >= threshold:
        #             # ith_score 为 是否为头
        #             ith_score = predict[ij[0], ij[1], 2:3]
        #             # 0.1 < ith_score < 0.9 TODO 不太理解这里的截取是在干嘛
        #             if not (cfg.trunc_threshold <= ith_score < 1 - cfg.trunc_threshold):
        #                 # 四舍五入取整
        #                 # np.around([-0.5,0.5,1.5,2.5,3.5,4.5])
        #                 # [-0.  0.  2.  2.  4.  4.]
        #                 ith = int(np.around(ith_score))
        #                 # 如果小于等于0.5，则total_score为前两个元素加分
        #                 # 如果大于0.5，则total_score为后两个元素加分
        #                 total_score[ith * 2:(ith + 1) * 2] += score
        #                 # 针对像素分别进行x和y的扩大
        #                 px = (ij[1] + 0.5) * cfg.pixel_size
        #                 py = (ij[0] + 0.5) * cfg.pixel_size
        #                 # 针对后四个坐标进行平移
        #                 p_v = [px, py] + np.reshape(predict[ij[0], ij[1], 3:7], (2, 2))
        #                 # TODO 不理解score*p_v是什么意思
        #                 # TODO 暂时的理解是，每个点都会预测所在文本框的左上角的坐标和右下角的坐标
        #                 # TODO 然后通过各自的分值作为置信度，头预测左上，尾预测右下，最后计算一个平均值
        #                 quad_list[g_th, ith * 2:(ith + 1) * 2] += score * p_v

        # score_list是头和尾对应的分值
        score_list[g_th] = total_score[:, 0]
        quad_list[g_th] /= (total_score + cfg.epsilon)

    return score_list, quad_list

def sort_group(predict, group, region_list, tag):
    tuple_list = []
    for row in group:
        if tag:
            min = 99999999
            for i,j in region_list[row]:
                score = predict[i, j, 1]
                ith_score = predict[i, j, 2:3]
                ith = int(np.around(ith_score))

                if score > cfg.side_vertex_pixel_threshold \
                        and not (cfg.trunc_threshold <= ith_score < 1 - cfg.trunc_threshold) \
                        and ith == 0\
                        and j < min :
                        min = j

            tuple_list.append([min, row])
        else:
            max = -1
            for i,j in region_list[row]:
                score = predict[i, j, 1]
                ith_score = predict[i, j, 2:3]
                ith = int(np.around(ith_score))
                if score > cfg.side_vertex_pixel_threshold \
                        and not (cfg.trunc_threshold <= ith_score < 1 - cfg.trunc_threshold) \
                        and ith == 1\
                        and j > max:
                    max = j
            tuple_list.append([max, row])


    tuple_list = np.array(tuple_list)
    tuple_list = tuple_list[tuple_list[:, 0].argsort()]
    if tag:
        return tuple_list[:,1]
    else:
        return tuple_list[:, 1][::-1]