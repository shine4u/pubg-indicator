import json
import logging
import os.path
from itertools import filterfalse
from dataclasses import dataclass, field
from typing import List
from pubg_indicator.req import ReqManager, URLPat

logger = logging.getLogger(__file__)

PROJ_DIR = '/Users/*/PycharmProjects/a/pubg-indicator'
api_key = '***'

cache_path = f'{PROJ_DIR}/cache'
server = 'https://api.pubg.com/'


req_mgr = ReqManager(
    pats=[
        URLPat('tournaments', server + 'tournaments'),
        URLPat('tournament', server + 'tournaments/{tournament_id}'),
        URLPat('match', server + 'shards/tournament/matches/{match_id}'),
        URLPat('telemetry', '{telemetry_url}', timeout=20),

    ],
    default_headers={
        'Accept': 'application/vnd.api+json',
        'Authorization': f'Bearer {api_key}',
    }
)




def get_tournaments(do_update=True):
    src_path = f'{cache_path}/tournaments.json'
    if not do_update and os.path.exists(src_path):
        return open(src_path, 'r').read()
    response = req_mgr.request(pat='tournaments')
    if not os.path.exists(src_path) or do_update:
        if response.status_code == 200:
            open(src_path, 'w').write(response.text)
    return response.text


def get_tournament(tournament_id: str, do_update=True) -> dict:
    src_path = f'{cache_path}/tournament.{tournament_id}.json'
    if not do_update and os.path.exists(src_path):
        tournament = json.loads(open(src_path, 'r').read())
    else:
        response = req_mgr.request(pat='tournament', tournament_id=tournament_id)
        if not os.path.exists(src_path) or do_update:
            if response.status_code == 200:
                open(src_path, 'w').write(response.text)
        tournament = response.json()
    return tournament


def get_match(match_id: str, with_telemetry=True, cache=True) -> dict:
    src_path = f'{cache_path}/match.{match_id}.json'
    if cache and os.path.exists(src_path):
        match = json.loads(open(src_path, 'r').read())
    else:
        response = req_mgr.request(pat='match', match_id=match_id)
        if cache:
            if response.status_code == 200:
                open(src_path, 'w').write(response.text)
        match = response.json()
    if with_telemetry:
        assert_info = next(filterfalse(lambda x: x['type'] != 'asset', match['included']))
        assert_url = assert_info['attributes']['URL']
        _get_telemetry(match_id=match_id, telemetry_url=assert_url, cache=cache)
    return match


def _get_telemetry(match_id: str, telemetry_url: str, cache=True):
    src_path = f'{cache_path}/match.{match_id}.telemetry.json'
    if cache and os.path.exists(src_path):
        match_data = open(src_path, 'r').read()
    else:
        response = req_mgr.request(pat='telemetry', telemetry_url=telemetry_url)
        if cache:
            if response.status_code == 200:
                open(src_path, 'w').write(response.text)
        match_data = response.text
    return match_data


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Circle:
    center: Point
    radius: float


MAX_TS = 9999

map_size_dic = {
    'Desert_Main': 800000,
    'Baltic_Main': 800000,
    'Tiger_Main': 400000,
    'Neon_Main': 400000,

}


@dataclass
class PlayInfo:
    name: str
    team_id: str
    kills: List[str] = field(default_factory=list)
    killed_by: str = field(default='')
    killed_ts: int = field(default=MAX_TS)
    quan_pos: List[Point] = field(default_factory=lambda: [None] * 10)
    quan_pos_ts: List[int] = field(default_factory=lambda: [9999] * 10)
    quan_score: List[int] = field(default_factory=lambda: [-1] * 10)

    def get_team_name(self) -> str:
        return self.name.split('_')[0]
