#!/usr/bin/env python3
"""
gMicroMC Web Configuration Interface
Ажиллуулах: python web_config.py
Нээх: http://localhost:8080
"""
import json, re, os, sys, struct
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.txt')
OUTPUT_DIR  = os.path.join(BASE_DIR, 'output')
HTML_FILE   = os.path.join(BASE_DIR, 'web_config.html')

SPECIES = ['e-','.OH','.H','H3O+','H2','OH-','H2O2','O2','.HO2','O2-','HO2-']
N_SPEC  = len(SPECIES)

# ── Config helpers ────────────────────────────────────────────────────────────

def strip_comments(text):
    return re.sub(r'//[^\n]*', '', text)

def read_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        raw = f.read()
    return json.loads(strip_comments(raw))

def write_config(data):
    def fmt(v):
        if isinstance(v, float):
            if abs(v) >= 1e6 or (abs(v) < 1e-3 and v != 0):
                return f"{v:g}"
            return repr(v)
        return json.dumps(v)
    lines = ['{',
        '//global setting',
        f'\t"Device": {fmt(data["Device"])},',
        f'\t"startStage": {fmt(data["startStage"])},',
        f'\t"outputDir": {fmt(data["outputDir"])},',
        f'\t"NPART": {fmt(data["NPART"])},',
        f'\t"NRAND": {fmt(data["NRAND"])},',
        f'\t"NTHREAD_PER_BLOCK": {fmt(data["NTHREAD_PER_BLOCK"])},',
        f'\t"verbose": {fmt(data["verbose"])},',
        f'\t"targetEneDep": {fmt(data["targetEneDep"])}, //eV',
        '',
        '//physics stage',
        f'\t"GPUBaseMemory": {fmt(data["GPUBaseMemory"])}, // in MB',
        f'\t"nSecondPer100keV": {fmt(data["nSecondPer100keV"])},',
        f'\t"nRadicalsPer100keV": {fmt(data["nRadicalsPer100keV"])},',
        '',
        f'\t"pCSData": {fmt(data["pCSData"])},',
        f'\t"eDACSData": {fmt(data["eDACSData"])},',
        f'\t"eIonCSData": {fmt(data["eIonCSData"])},',
        f'\t"eExcCSData": {fmt(data["eExcCSData"])},',
        f'\t"eElaCSData": {fmt(data["eElaCSData"])},',
        f'\t"eElaDCSData": {fmt(data["eElaDCSData"])},',
        '',
        f'\t"eECutoff": {fmt(data["eECutoff"])}, //eV',
        f'\t"pECutoff": {fmt(data["pECutoff"])},',
        '',
        f'\t"physicsWorldShape": {fmt(data["physicsWorldShape"])},',
        f'\t"physicsWorldSizeX": {fmt(data["physicsWorldSizeX"])}, // in cm',
        f'\t"physicsWorldSizeY": {fmt(data["physicsWorldSizeY"])},',
        f'\t"physicsWorldSizeZ": {fmt(data["physicsWorldSizeZ"])},',
        f'\t"physicsWorldCenterX": {fmt(data["physicsWorldCenterX"])}, // in cm',
        f'\t"physicsWorldCenterY": {fmt(data["physicsWorldCenterY"])},',
        f'\t"physicsWorldCenterZ": {fmt(data["physicsWorldCenterZ"])},',
        '',
        f'\t"ROIShape": {fmt(data["ROIShape"])},',
        f'\t"ROISizeX": {fmt(data["ROISizeX"])}, // in um',
        f'\t"ROISizeY": {fmt(data["ROISizeY"])},',
        f'\t"ROISizeZ": {fmt(data["ROISizeZ"])},',
        f'\t"ROICenterX": {fmt(data["ROICenterX"])}, // in um',
        f'\t"ROICenterY": {fmt(data["ROICenterY"])},',
        f'\t"ROICenterZ": {fmt(data["ROICenterZ"])},',
        '',
        f'\t"nPar": {fmt(data["nPar"])},',
        f'\t"maxRun": {fmt(data["maxRun"])},',
        f'\t"sourceModel": {fmt(data["sourceModel"])},',
        f'\t"sourceEnergyModel": {fmt(data["sourceEnergyModel"])},',
        f'\t"sourceFile": {fmt(data["sourceFile"])},',
        f'\t"sourceSampleDim": {fmt(data["sourceSampleDim"])},',
        f'\t"sourcePType": {fmt(data["sourcePType"])},',
        f'\t"sourceA": {fmt(data["sourceA"])},',
        f'\t"sourceEmin": {fmt(data["sourceEmin"])}, //eV',
        f'\t"sourceEmax": {fmt(data["sourceEmax"])},',
        '',
        f'\t"fileForIntOutput": {fmt(data["fileForIntOutput"])},',
        f'\t"fileForFloatOutput": {fmt(data["fileForFloatOutput"])},',
        f'\t"fileForTotalEvent": {fmt(data["fileForTotalEvent"])},',
        f'\t"fileForEnergy": {fmt(data["fileForEnergy"])},',
        '',
        '//physicochemcial stage',
        f'\t"fileForBranchInfo": {fmt(data["fileForBranchInfo"])},',
        f'\t"fileForRecombineInfo": {fmt(data["fileForRecombineInfo"])},',
        f'\t"fileForIntInput": {fmt(data["fileForIntInput"])},',
        f'\t"fileForFloatInput": {fmt(data["fileForFloatInput"])},',
        f'\t"fileForOutput": {fmt(data["fileForOutput"])},',
        '',
        '//chemical stage',
        f'\t"fileForSpecInfo": {fmt(data["fileForSpecInfo"])},',
        f'\t"fileForReactionInfo": {fmt(data["fileForReactionInfo"])},',
        f'\t"useConstantRadius": {fmt(data["useConstantRadius"])},',
        f'\t"fileForRadicalInfo": {fmt(data["fileForRadicalInfo"])},',
        f'\t"chemicalTime": {fmt(data["chemicalTime"])}, //ps',
        f'\t"DNAReactTime": {fmt(data["DNAReactTime"])}, //ps',
        f'\t"timeFileForNvsTime": {fmt(data["timeFileForNvsTime"])},',
        f'\t"numberFileForNvsTime": {fmt(data["numberFileForNvsTime"])},',
        f'\t"saveInterval": {fmt(data["saveInterval"])}, //ps',
        f'\t"chemROI": {fmt(data["chemROI"])}, //nm',
        f'\t"fileForChemOutput": {fmt(data["fileForChemOutput"])},',
        '',
        '//DNA related',
        f'\t"bentChromatin": {fmt(data["bentChromatin"])},',
        f'\t"bentHistone": {fmt(data["bentHistone"])},',
        f'\t"straightChromatin": {fmt(data["straightChromatin"])},',
        f'\t"straightHistone": {fmt(data["straightHistone"])},',
        f'\t"wholeDNA": {fmt(data["wholeDNA"])},',
        '',
        f'\t"fileForChemPos": {fmt(data["fileForChemPos"])},',
        f'\t"fileForOutputDamage": {fmt(data["fileForOutputDamage"])},',
        f'\t"compareEnergy": {fmt(data["compareEnergy"])}, // in eV',
        f'\t"repTimes": {fmt(data["repTimes"])},',
        f'\t"probChem": {fmt(data["probChem"])}',
        '}']
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

# ── Results readers ───────────────────────────────────────────────────────────

def read_phy_energy():
    p = os.path.join(OUTPUT_DIR, 'phyEne.txt')
    if not os.path.exists(p):
        return None
    rows = []
    with open(p) as f:
        for line in f:
            pts = line.strip().split()
            if len(pts) >= 2:
                rows.append({'energy_eV': float(pts[0]), 'LET': float(pts[1])})
    return rows or None

def read_source():
    p = os.path.join(OUTPUT_DIR, 'totalsource.txt')
    if not os.path.exists(p):
        return None
    rows = []
    with open(p) as f:
        for line in f:
            pts = line.strip().split()
            if len(pts) >= 7:
                rows.append({
                    'index': int(pts[0]),
                    'x': float(pts[1]), 'y': float(pts[2]), 'z': float(pts[3]),
                    'dx': float(pts[4]), 'dy': float(pts[5]), 'dz': float(pts[6]),
                    'energy_eV': float(pts[7]) if len(pts) > 7 else None
                })
    return rows or None

def read_chem_nvstime():
    tf = os.path.join(OUTPUT_DIR, 'Time.dat')
    nf = os.path.join(OUTPUT_DIR, 'nRadical.dat')
    if not os.path.exists(tf) or not os.path.exists(nf):
        return None
    with open(tf, 'rb') as f: raw = f.read()
    n_steps = len(raw) // 4
    if n_steps == 0: return None
    times = list(struct.unpack(f'{n_steps}f', raw))
    with open(nf, 'rb') as f: raw2 = f.read()
    vps = 2 * N_SPEC
    n2 = len(raw2) // (4 * vps)
    if n2 == 0: return None
    counts = struct.unpack(f'{n2 * vps}i', raw2)
    result = []
    for i in range(min(n_steps, n2)):
        row = {'time_ps': times[i]}
        for j, sp in enumerate(SPECIES):
            row[sp] = counts[i * vps + j]
        result.append(row)
    return result or None

def read_dna_damage():
    p = os.path.join(OUTPUT_DIR, 'finalstat.txt')
    if not os.path.exists(p):
        return None
    lines = [l.strip() for l in open(p) if l.strip()]
    result = []
    i = 0
    while i < len(lines) - 1:
        if 'SSBd' in lines[i] or ('SSB' in lines[i] and 'DSB' in lines[i]):
            try:
                vals = list(map(int, lines[i+1].split()))
                result.append({'type': 'damage' if 'SSBd' in lines[i] else 'complexity',
                               'labels': lines[i].split(), 'values': vals})
            except ValueError:
                pass
            i += 2
        else:
            i += 1
    return result or None

# ── HTTP handler ──────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("  %s %s" % (args[0], args[1]))

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/config':
            try:    self.send_json(read_config())
            except Exception as e: self.send_json({'error': str(e)}, 500)
        elif path == '/api/results':
            try:
                self.send_json({
                    'physics': {'energy': read_phy_energy(), 'source': read_source()},
                    'chem':    read_chem_nvstime(),
                    'dna':     read_dna_damage(),
                })
            except Exception as e: self.send_json({'error': str(e)}, 500)
        else:
            with open(HTML_FILE, 'rb') as f:
                body = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)

    def do_POST(self):
        if urlparse(self.path).path == '/api/config':
            try:
                n = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(n))
                write_config(data)
                self.send_json({'ok': True})
            except Exception as e:
                self.send_json({'ok': False, 'error': str(e)}, 500)
        else:
            self.send_json({'error': 'Not found'}, 404)

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = 8080
    server = HTTPServer(('localhost', port), Handler)
    print("""
+----------------------------------------------+
|   gMicroMC Web Configuration Interface       |
|   Хаяг  : http://localhost:8080              |
|   Зогсоох: Ctrl+C                            |
+----------------------------------------------+
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("  Сервер зогсоов.")
        sys.exit(0)
