import math
import re
from datetime import datetime
from collections import Counter
from typing import Dict, Tuple
from collections import defaultdict
from pubg_indicator.deps import *
from loguru import logger


team_data_all = defaultdict(list)
f_tot = open(f'quan_score.csv', 'w')


def parse_telemetry(match_id: str, f):
    src_path = f'{cache_path}/match.{match_id}.telemetry.json'
    match_data = json.loads(open(src_path, 'r').read())

    counter = Counter()

    quan_lst: List[Tuple[Circle, int]] = []  # 第0个圈是以地图中间点为圆心的圈
    players: Dict[str, PlayInfo] = {}  # 玩家数据 key为name

    last_quan_r, last_quan_ts = -1, -1  # LogGameStatePeriodic
    for event in match_data:
        counter[event['_T']] += 1
        ts = datetime.strptime(re.sub(r'\.\d+Z', '', event['_D']), '%Y-%m-%dT%H:%M:%S')  # 2024-06-28T13:45:35.074Z
        if '4AM_ZpYan1XX' in json.dumps(event):
            logger.info(f'AAA {event["_T"]} {event}')

        if event['_T'] == 'LogPlayerCreate':
            # {'character': {'name': 'CCG_YuYu', 'teamId': 5, 'health': 100, 'location': {'x': 723736.4375, 'y': 431904.15625, 'z': 2839.682373046875}, 'ranking': 0, 'individualRanking': 0, 'accountId': 'account.37ce0e9b2b384e479f91799c2a1bd9ec', 'isInBlueZone': False, 'isInRedZone': False, 'zone': [], 'type': 'user'}, 'common': {'isGame': 0}, '_D': '2024-06-28T13:24:10.358Z', '_T': 'LogPlayerCreate'}
            player_name = event['character']['name']
            players[player_name] = PlayInfo(name=player_name, team_id=event['character']['teamId'])
        elif event['_T'] == 'LogMatchStart':
            print(event)
            match_start_ts = ts
            map_name = event['mapName']
            quan_lst.append((Circle(Point(map_size_dic[map_name]/2, map_size_dic[map_name]/2), map_size_dic[map_name]), 0))

        elif event['_T'] == 'LogPhaseChange':
            pass
        elif event['_T'] == 'LogPlayerPosition':
            pass
        elif event['_T'] == 'LogPlayerKillV2':
            # {'attackId': 419430743, 'dBNOId': -1, 'victimGameResult': {'rank': 9, 'gameResult': '', 'teamId': 12, 'stats': {'killCount': 2, 'distanceOnFoot': 2279.58251953125, 'distanceOnSwim': 0, 'distanceOnVehicle': 3420.356689453125, 'distanceOnParachute': 325.068115234375, 'distanceOnFreefall': 1533.6693115234375, 'bpRewardDetail': {'byPlayTime': 0, 'byRanking': 0, 'byKills': 0, 'byDamageDealt': 0, 'boostAmount': 0, 'byModeScore': 0}, 'arcadeRewardDetail': {'byPlayTime': 0}, 'statTrakDataPairs': [], 'headshotStatTrakDataPairs': []}, 'accountId': 'account.c4bab608885b405586387e257aa70b90', 'isRewardAbuse': False}, 'victim': {'name': 'CTG_Hang2y', 'teamId': 12, 'health': 0, 'location': {'x': 454523.1875, 'y': 390202.15625, 'z': 10318.6201171875}, 'ranking': 9, 'individualRanking': 23, 'accountId': 'account.c4bab608885b405586387e257aa70b90', 'isInBlueZone': False, 'isInRedZone': False, 'zone': [], 'type': 'user'}, 'victimWeapon': 'WeapAUG_C_30', 'victimWeaponAdditionalInfo': ['Item_Attach_Weapon_Upper_DotSight_01_C', 'Item_Attach_Weapon_Muzzle_FlashHider_Large_C', 'Item_Attach_Weapon_Magazine_QuickDraw_Large_C', 'Item_Attach_Weapon_Lower_Foregrip_C'], 'dBNOMaker': None, 'dBNODamageInfo': {'damageReason': 'NonSpecific', 'damageTypeCategory': 'Damage_None', 'damageCauserName': 'None', 'additionalInfo': [], 'distance': -1, 'isThroughPenetrableWall': False}, 'finisher': {'name': 'SMS_Monsters', 'teamId': 8, 'health': 28.373685836791992, 'location': {'x': 459565.84375, 'y': 386666.90625, 'z': 10167.849609375}, 'ranking': 0, 'individualRanking': 0, 'accountId': 'account.c78a06fc4ba5421abbb9ec49af2f6ec6', 'isInBlueZone': False, 'isInRedZone': False, 'zone': [], 'type': 'user'}, 'finishDamageInfo': {'damageReason': 'TorsoShot', 'damageTypeCategory': 'Damage_Gun', 'damageCauserName': 'WeapBerylM762_C', 'additionalInfo': ['Item_Attach_Weapon_Muzzle_Compensator_Large_C', 'Item_Attach_Weapon_Lower_Foregrip_C', 'Item_Attach_Weapon_Upper_DotSight_01_C', 'Item_Attach_Weapon_Magazine_QuickDraw_Large_C'], 'distance': 6160.28466796875, 'isThroughPenetrableWall': False}, 'killer': {'name': 'SMS_Monsters', 'teamId': 8, 'health': 28.373685836791992, 'location': {'x': 459565.84375, 'y': 386666.90625, 'z': 10167.849609375}, 'ranking': 0, 'individualRanking': 0, 'accountId': 'account.c78a06fc4ba5421abbb9ec49af2f6ec6', 'isInBlueZone': False, 'isInRedZone': False, 'zone': [], 'type': 'user'}, 'killerDamageInfo': {'damageReason': 'TorsoShot', 'damageTypeCategory': 'Damage_Gun', 'damageCauserName': 'WeapBerylM762_C', 'additionalInfo': ['Item_Attach_Weapon_Muzzle_Compensator_Large_C', 'Item_Attach_Weapon_Lower_Foregrip_C', 'Item_Attach_Weapon_Upper_DotSight_01_C', 'Item_Attach_Weapon_Magazine_QuickDraw_Large_C'], 'distance': 6160.28466796875, 'isThroughPenetrableWall': False}, 'assists_AccountId': [], 'teamKillers_AccountId': [], 'isSuicide': False, 'common': {'isGame': 4.5}, '_D': '2024-06-28T13:45:35.074Z', '_T': 'LogPlayerKillV2'}
            suicide: bool = event['isSuicide']
            victim = event['victim']['name']
            killer = (event['killer'] or {}).get('name', victim) if not suicide else victim
            finisher = (event['finisher'] or {}).get('name', victim)
            # logger.info(f'{victim:20s} {killer:20s} {finisher:20s}')
            if not suicide:
                # logger.info(event)
                if players[finisher].team_id == players[killer].team_id:
                    players[killer].kills.append(victim)
                    players[victim].killed_by = killer
                    players[victim].killed_ts = ts
                else:
                    players[finisher].kills.append(victim)
                    players[victim].killed_by = finisher
                    players[victim].killed_ts = ts

                # dx = event['killer']['location']['x'] - event['victim']['location']['x']
                # dy = event['killer']['location']['y'] - event['victim']['location']['y']
                # dz = event['killer']['location']['z'] - event['victim']['location']['z']
                # distance = math.sqrt(dx * dx + dy * dy + dz * dz)
                # reason = event['finishDamageInfo']['damageTypeCategory']
                # logger.info(f'PLAY RESULT {victim} | {killer} {reason} {distance}')
            else:
                # logger.info(event)
                players[victim].killed_by = killer
            pass
        elif event['_T'] == 'LogPlayerMakeGroggy':
            # print(event)
            attacker, victim = event['attacker']['name'], event['victim']['name']
            # print(ts, attacker, victim)
        elif event['_T'] == 'LogGameStatePeriodic':
            # 每隔10秒的地图状态
            # logger.info(event)
            # logger.info((ts - match_start_ts).total_seconds())
            ts = event['gameState']['elapsedTime']
            x = event['gameState']['poisonGasWarningPosition']['x']
            y = event['gameState']['poisonGasWarningPosition']['y']
            r = event['gameState']['poisonGasWarningRadius']
            if r == last_quan_r and r > 0 and (len(quan_lst) == 1 or quan_lst[-1][0].radius != r):
                quan_lst.append((Circle(Point(x, y), r), last_quan_ts))
            last_quan_ts, last_quan_r = ts, r
    logger.info(counter)

    # for name, player in players.items():
    #     logger.info(f'PLAYER {name} {player}')

    # 第二轮
    # 1、获取每个玩家在每个圈开始时候的位置
    for event in match_data:
        if event['_T'] == 'LogPlayerPosition':
            # {'character': {'name': 'RBS_Hush', 'teamId': 15, 'health': 100, 'location': {'x': 490481.78125, 'y': 479688.125, 'z': 684.419677734375}, 'ranking': 0, 'individualRanking': 0, 'accountId': 'account.16e25cbd548b4a278413956981372e8f', 'isInBlueZone': False, 'isInRedZone': False, 'zone': [], 'type': 'user'}, 'vehicle': {'vehicleType': 'WheeledVehicle', 'vehicleId': 'Dacia_A_01_v2_C', 'seatIndex': 0, 'healthPercent': 98.94912719726562, 'feulPercent': 29.962657928466797, 'altitudeAbs': 0, 'altitudeRel': 0, 'velocity': 2385.50537109375, 'isWheelsInAir': False, 'isInWaterVolume': False, 'isEngineOn': True}, 'elapsedTime': 836, 'numAlivePlayers': 54, 'common': {'isGame': 3}, '_D': '2024-06-28T13:40:19.176Z', '_T': 'LogPlayerPosition'}
            # print(event)
            name = event['character']['name']
            x, y, ts = event['character']['location']['x'], event['character']['location']['y'], event['elapsedTime']
            for quan_id in range(1, len(quan_lst)):
                quan_center, quan_ts = quan_lst[quan_id]
                if ts > quan_ts - 10 and abs(quan_ts - ts) < abs(quan_ts - players[name].quan_pos_ts[quan_id]):
                    players[name].quan_pos[quan_id] = Point(x, y)
                    players[name].quan_pos_ts[quan_id] = quan_ts

    # for name in sorted(player_stat.keys()):
    #     print(f'{name} {player_stat[name]}')

    # 每个圈每个队伍单独打分
    quan_weight = [1.0, 0.4, 0.6, 0.9, 1.1, 1.2, 1.4, 1.6, 1.8, 2.0]
    team_data = {}
    for quan_id in range(1, len(quan_lst)):
        def get_player_dist(player_, quan_) -> float:
            dx, dy = quan_.center.x - player_.quan_pos[quan_id].x, quan_.center.y - player_.quan_pos[quan_id].y
            distance = math.sqrt(dx * dx + dy * dy)
            return distance

        players_by_lst_quan: List[Tuple[float, PlayInfo]] = []
        players_by_cur_quan: List[Tuple[float, PlayInfo]] = []
        for name, player in players.items():
            # already killed
            if not player.quan_pos[quan_id]:
                continue
            players_by_lst_quan.append((get_player_dist(player, quan_lst[quan_id - 1][0]), player))
            players_by_cur_quan.append((get_player_dist(player, quan_lst[quan_id][0]), player))
        players_by_lst_quan.sort()
        players_by_cur_quan.sort()

        player_rank_data = {}
        for idx, (dist, player) in enumerate(players_by_lst_quan):
            player_rank_data[player.name] = {'from': idx}
        for idx, (dist, player) in enumerate(players_by_cur_quan):
            player_rank_data[player.name]['to'] = idx

        # 队伍圈运
        team_quan_data = defaultdict(list)
        for name, rank in player_rank_data.items():
            player = players[name]

            def adj_rank(_rank):
                return math.pow(_rank, 0.8)

            delta_rank = adj_rank(rank['from']) - adj_rank(rank['to'])
            team_quan_data[player.get_team_name()].append(delta_rank)
            logger.info(f'{player.get_team_name()} {rank["from"]}->{rank["to"]}')

        for team_name, ranks in team_quan_data.items():
            weight_adjust = [1, 0.15, 0.4, 0.75, 1.0]
            # weight_adjust = [1, 1.0, 1.0, 1.0, 1.0]
            score = sum(ranks)/len(ranks)/len(players_by_cur_quan) * quan_weight[quan_id]
            score_adjust = score * weight_adjust[len(ranks)]
            logger.info(f'{quan_id} {team_name} {score} {score_adjust}')
            if team_name not in team_data:
                team_data[team_name] = ['-'] * 10
            team_data[team_name][quan_id] = str(score_adjust)
    for team_name, scores in team_data.items():
        output = [team_name]
        output += list(str(x) for x in scores[1:9])
        team_data_all[team_name].append(sum(float(score) for score in scores[1:9] if score != '-'))
        f.write(','.join(output) + '\n')
        logger.info(f'{team_name} {scores}')
    f.close()


def main():
    get_tournaments(do_update=False)
    tournament = get_tournament(tournament_id='as-ewc24fs', do_update=False)
    matches = []
    for item in tournament['included']:
        if item['type'] != 'match':
            continue
        match_id = item['id']
        match_ts: str = item['attributes']['createdAt']
        if match_ts[:10] not in ['2024-08-25', '2024-08-24']:
            continue
        if match_id in ['9baf0d44-a820-42ab-a506-ad9462a164ff']:
            continue
        matches.append((match_ts, match_id))
    matches = sorted(matches)
    logger.info(matches)
    for _match_id, (match_ts, match_id) in enumerate(sorted(matches)):
        # if match_id != '85b9ff58-9a60-4ecd-b76f-88e0bf1508d1':
        #     continue
        logger.info(f'match_id={match_id} match_ts={match_ts}')
        get_match(match_id=match_id, with_telemetry=True)
        f = open(f'quan_score.{_match_id}.csv', 'w')
        parse_telemetry(match_id, f)
    for team_name, team_scores in team_data_all.items():
        output = [team_name]
        output += list(str(x) for x in team_scores)
        f_tot.write(','.join(output) + '\n')


if __name__ == '__main__':
    main()
