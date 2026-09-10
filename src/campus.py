"""定位签到护栏：每日签前校验坐标必须落在校区范围内。

说明：
- 服务端 check.action 本身会做精确多边形围栏校验，本模块是「软约束 + 快速失败」：
  在发起任何签到请求前，先判断配置的坐标是否落在校区边界盒内，
  明显填错（如填了老家/异地坐标）会直接拦截并推送提醒，不发签到请求。
- 边界盒为宽泛范围（GCJ-02 高德坐标系），用于拦截明显越界的坐标，
  精确判定仍以服务端围栏为准。
- 如需支持其他校区，在 config.yaml 的 campus.bounds 里按同样格式追加即可。
"""

# 旗山校区边界盒（GCJ-02，含生活区；取宽泛范围防误拦，精确围栏由服务端判定）
DEFAULT_BOUNDS = {
    "旗山校区": {
        "min_lng": 119.17, "max_lng": 119.23,
        "min_lat": 26.03, "max_lat": 26.08,
    },
}


def get_bounds(cfg: dict) -> dict:
    """读取校区边界盒配置，未配置时用内置默认。"""
    bounds = (cfg.get("campus") or {}).get("bounds")
    if not bounds:
        return DEFAULT_BOUNDS
    return bounds


def match_campus(longitude: float, latitude: float, cfg: dict):
    """返回命中的校区名；坐标不在任何校区范围内返回 None。"""
    for name, box in get_bounds(cfg).items():
        try:
            if (box["min_lng"] <= longitude <= box["max_lng"]
                    and box["min_lat"] <= latitude <= box["max_lat"]):
                return name
        except (KeyError, TypeError):
            continue
    return None
