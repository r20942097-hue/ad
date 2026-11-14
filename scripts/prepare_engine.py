"""Download verified, pinned uBO and PSL snapshots for optional Node.js checks."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import sys
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'verification/engine-lock.json'


def download(url, digest, target, cap):
    if target.is_symlink():
        raise ValueError('download target must not be a symlink')
    if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == digest:
        return target.read_bytes()
    request = urllib.request.Request(url, headers={'User-Agent': 'filter-engine-verification'})
    with urllib.request.urlopen(request, timeout=45) as response:
        content = response.read(cap + 1)
    if len(content) > cap:
        raise ValueError('download exceeds size limit')
    if hashlib.sha256(content).hexdigest() != digest:
        raise ValueError('download SHA256 does not match engine lock')
    target.write_bytes(content)
    return content


def extract_snapshot(content, directory, commit):
    expected = 'uBlock-' + commit
    with tarfile.open(fileobj=io.BytesIO(content), mode='r:gz') as archive:
        for member in archive.getmembers():
            path = Path(member.name)
            if (path.is_absolute() or '..' in path.parts or not path.parts
                    or path.parts[0] != expected or member.issym() or member.islnk()
                    or not (member.isdir() or member.isfile())):
                raise ValueError('unsafe archive member')
        archive.extractall(directory, filter='data') if hasattr(tarfile, 'data_filter') else archive.extractall(directory)
    return directory / expected


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def validate_lock(lock):
    if not isinstance(lock, dict) or lock.get('schema') != 'filter-engine-lock/v1':
        raise ValueError('unsupported engine lock')
    for key in ('ublock', 'public_suffix'):
        record = lock.get(key)
        if (not isinstance(record, dict)
                or not isinstance(record.get('commit'), str)
                or not re.fullmatch(r'[0-9a-f]{40}', record['commit'])
                or not isinstance(record.get('sha256'), str)
                or not re.fullmatch(r'[0-9a-f]{64}', record['sha256'])):
            raise ValueError('invalid engine snapshot identity')
    ubo, psl = lock['ublock'], lock['public_suffix']
    if (ubo.get('repository') != 'gorhill/uBlock'
            or ubo.get('archive_url') != f"https://codeload.github.com/gorhill/uBlock/tar.gz/{ubo['commit']}"):
        raise ValueError('uBO archive must match the official pinned repository')
    if (psl.get('repository') != 'publicsuffix/list'
            or psl.get('path') != 'public_suffix_list.dat'
            or psl.get('url') != f"https://raw.githubusercontent.com/publicsuffix/list/{psl['commit']}/public_suffix_list.dat"):
        raise ValueError('PSL URL must match the official pinned repository')


def prepare(directory, lock):
    validate_lock(lock)
    if directory.is_symlink() or (directory / 'node').is_symlink() or (directory / 'sources').is_symlink() or (directory / 'manifest.json').is_symlink():
        raise ValueError('engine directory must not be a symlink')
    directory.mkdir(parents=True, exist_ok=True)
    ubo = lock['ublock']
    content = download(ubo['archive_url'], ubo['sha256'], directory / 'source.tar.gz', 32_000_000)
    source = extract_snapshot(content, directory / 'sources', ubo['commit'])
    node = directory / 'node'
    node.mkdir(exist_ok=True)
    shutil.copytree(source / 'src/js', node / 'js', dirs_exist_ok=True)
    shutil.copytree(source / 'src/lib', node / 'lib', dirs_exist_ok=True)
    shutil.copy2(source / 'platform/nodejs/index.js', node / 'index.js')
    shutil.copy2(source / 'LICENSE.txt', node / 'LICENSE.txt')
    (node / 'package.json').write_text('{"type":"module"}\n', encoding='utf-8', newline='\n')
    psl = lock['public_suffix']
    download(psl['url'], psl['sha256'], directory / 'public_suffix_list.dat', 2_000_000)
    manifest = {'ublock_commit': ubo['commit'], 'source': str(source.resolve()),
                'lock_sha256': hashlib.sha256(json.dumps(lock, sort_keys=True).encode()).hexdigest(),
                'files': {path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in sorted(node.rglob('*')) if path.is_file()}}
    manifest['files']['public_suffix_list.dat'] = psl['sha256']
    (directory / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.directory.is_symlink() or LOCK.is_symlink():
            raise ValueError('engine directory must not be a symlink')
        manifest = prepare(args.directory.resolve(), json.loads(LOCK.read_text(encoding='utf-8'), object_pairs_hook=_reject_duplicate_keys))
    except (OSError, ValueError, KeyError, tarfile.TarError) as exc:
        print('ENGINE PREPARATION FAILED:', exc, file=sys.stderr)
        return 1
    print('ENGINE PREPARATION PASSED:', manifest['ublock_commit'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
