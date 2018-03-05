import sys
import time

def pretty_time(seconds):
    seconds = int(round(seconds))
    s = seconds % 60
    m = (seconds / 60) % 60
    h = (seconds / 3600)
    return '%d:%02d:%02d' % (h, m, s)

class Bar(object):

    def __init__(self, max_value=100, min_value=0, enabled=True):
        self.min_value = min_value
        self.max_value = max_value
        self.value = min_value
        self.start_time = time.time()
        self.end_time = None
        self.enabled = enabled

    @property
    def percent_complete(self):
        return 100.0 * (self.value - self.min_value) / (self.max_value - self.min_value)

    @property
    def elapsed_time(self):
        return time.time() - self.start_time

    @property
    def eta(self):
        if self.percent_complete == 0:
            return 0
        return (1 - self.percent_complete / 100.0) * self.elapsed_time / (self.percent_complete / 100.0)

    def __call__(self, sequence):
        self.min_value = 0
        self.max_value = len(sequence)
        for i, item in enumerate(sequence):
            self.update(i)
            yield item
        self.done()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def increment(self, delta):
        self.update(self.value + delta)

    def update(self, value):
        self.value = value
        if self.enabled:
            sys.stdout.write('  %s    \r' % self.render())
            sys.stdout.flush()

    def done(self):
        self.update(self.max_value)
        self.stop()

    def stop(self):
        sys.stdout.write('\n')
        sys.stdout.flush()

    def render(self):
        items = [
            self.render_percent_complete(),
            self.render_value(),
            self.render_bar(),
            self.render_elapsed_time(),
            self.render_eta(),
        ]
        return ' '.join(items)

    def render_percent_complete(self):
        return '%3.0f%%' % self.percent_complete

    def render_value(self):
        if self.min_value == 0:
            return '(%g of %g)' % (self.value, self.max_value)
        else:
            return '(%g)' % (self.value)

    def render_bar(self, size=30):
        a = int(round(self.percent_complete / 100.0 * size))
        b = size - a
        return '[' + '#' * a + '-'  * b + ']'

    def render_elapsed_time(self):
        return pretty_time(self.elapsed_time)

    def render_eta(self):
        return pretty_time(self.eta)

if __name__ == '__main__':
    bar = Bar()
    for i in bar(range(3517)):
        time.sleep(0.001)
    with Bar(1) as bar:
        for i in range(100):
            bar.update(i / 100.0)
            time.sleep(0.01)
        bar.done()
