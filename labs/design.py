"""Small deterministic models: not distributed production implementations."""
from dataclasses import dataclass
import sqlite3

@dataclass
class TokenBucket:
    capacity: float
    rate: float
    tokens: float
    updated: float = 0

    def allow(self, now, cost=1):
        if now < self.updated or cost <= 0:
            raise ValueError('monotonic time and positive cost required')
        self.tokens = min(self.capacity, self.tokens + (now-self.updated)*self.rate)
        self.updated = now
        if self.tokens < cost:
            return False
        self.tokens -= cost
        return True

class Reservations:
    """Single-process SQLite teaching model; connection serializes operations."""
    def __init__(self, stock):
        self.db = sqlite3.connect(':memory:')
        self.db.executescript('CREATE TABLE stock(id INTEGER PRIMARY KEY, n INTEGER CHECK(n>=0)); CREATE TABLE holds(key TEXT PRIMARY KEY, quantity INTEGER);')
        self.db.execute('INSERT INTO stock VALUES(1,?)',(stock,))
        self.db.commit()

    def reserve(self, key, quantity):
        if quantity <= 0: raise ValueError('positive quantity required')
        with self.db:
            existing=self.db.execute('SELECT quantity FROM holds WHERE key=?',(key,)).fetchone()
            if existing:
                if existing[0] != quantity: raise ValueError('key reused with different payload')
                return True
            changed=self.db.execute('UPDATE stock SET n=n-? WHERE id=1 AND n>=?',(quantity,quantity)).rowcount
            if not changed: return False
            self.db.execute('INSERT INTO holds VALUES(?,?)',(key,quantity))
            return True

    @property
    def remaining(self): return self.db.execute('SELECT n FROM stock').fetchone()[0]

class FencedJob:
    """A lease epoch fences writes in this same state store, not arbitrary effects."""
    def __init__(self): self.epoch=0; self.result=None
    def claim(self): self.epoch+=1; return self.epoch
    def complete(self, epoch, result):
        if epoch != self.epoch or self.result is not None: return False
        self.result=result
        return True

if __name__=='__main__':
    r=Reservations(1)
    assert r.reserve('request-1',1)
    assert r.reserve('request-1',1)  # response lost, same logical retry
    assert not r.reserve('request-2',1)
    assert r.remaining == 0
    bucket=TokenBucket(2,1,2)
    assert [bucket.allow(0) for _ in range(3)] == [True,True,False]
    assert bucket.allow(1)
    job=FencedJob(); stale=job.claim(); current=job.claim()
    assert not job.complete(stale,'late')
    assert job.complete(current,'current')
    print('Reservation retry, token refill and stale-worker models passed')
