package main

import (
	"fmt"
	"math"
	"os"
	"sort"
)

const (
	// D = math.Pi
	S = 2
)

type Point struct {
	X, Y float64
}

func (a Point) Lerp(b Point, t float64) Point {
	x := a.X + (b.X-a.X)*t
	y := a.Y + (b.Y-a.Y)*t
	return Point{x, y}
}

type Segment struct {
	P0, P1 Point
}

type Circle struct {
	X, Y, R float64
}

func (c Circle) ContainsPoint(p Point) bool {
	return math.Hypot(p.X-c.X, p.Y-c.Y) < c.R
}

func (c Circle) Discretize(n int) []Point {
	points := make([]Point, n)
	for i := range points {
		t := float64(i) / float64(n-1)
		a := 2 * math.Pi * t
		x := math.Cos(a)*c.R + c.X
		y := math.Sin(a)*c.R + c.Y
		points[i] = Point{x, y}
	}

	return points
}

func (c Circle) IntersectLine(p0, p1 Point) (float64, float64, bool) {
	dx := p1.X - p0.X
	dy := p1.Y - p0.Y
	A := dx*dx + dy*dy
	B := 2 * (dx*(p0.X-c.X) + dy*(p0.Y-c.Y))
	C := (p0.X-c.X)*(p0.X-c.X) + (p0.Y-c.Y)*(p0.Y-c.Y) - c.R*c.R
	det := B*B - 4*A*C
	if A <= 0 || det <= 0 {
		return 0, 0, false
	}
	t0 := (-B + math.Sqrt(det)) / (2 * A)
	t1 := (-B - math.Sqrt(det)) / (2 * A)
	return t0, t1, true
}

func makeCircles(circleRadius, visibleRadius float64) []Circle {
	var circles []Circle
	a := int(math.Ceil(circleRadius + visibleRadius))
	for y := -a; y <= a; y++ {
		for x := -a; x <= a; x++ {
			cx := float64(x)
			cy := float64(y)
			if math.Hypot(cx, cy) <= circleRadius+visibleRadius {
				circles = append(circles, Circle{cx, cy, circleRadius})
			}
		}
	}
	return circles
}

func count(circles []Circle, p Point) int {
	var result int
	for _, c := range circles {
		if c.ContainsPoint(p) {
			result++
		}
	}
	return result
}

type splitFunc func(Point) bool

func split(circles []Circle, p0, p1 Point, f splitFunc) []Segment {
	var ts []float64
	for _, c := range circles {
		t0, t1, ok := c.IntersectLine(p0, p1)
		if ok {
			ts = append(ts, t0)
			ts = append(ts, t1)
		}
	}
	sort.Float64s(ts)
	var segments []Segment
	for i := 1; i < len(ts); i++ {
		t0 := ts[i-1]
		t1 := ts[i]
		if t1 < 0 || t0 > 1 {
			continue
		}
		t0 = math.Max(t0, 0)
		t1 = math.Min(t1, 1)
		t := (t0 + t1) / 2
		p := p0.Lerp(p1, t)
		if f(p) {
			q0 := p0.Lerp(p1, t0)
			q1 := p0.Lerp(p1, t1)
			segments = append(segments, Segment{q0, q1})
		}
	}
	return segments
}

func run(path string, d, s float64) error {
	file, err := os.Create(path)
	if err != nil {
		return err
	}

	circles := makeCircles(d/2, s*math.Sqrt(2))

	x0 := -s
	x1 := s
	y0 := -s
	y1 := s

	f := func(p Point) bool {
		return count(circles, p)%2 == 1
	}

	g := func(p Point) bool {
		return math.Hypot(p.X, p.Y) <= s
	}
	outer := []Circle{Circle{0, 0, s}}

	const n = 200
	for i := 0; i <= n; i++ {
		t := float64(i) / float64(n)
		y := y0 + (y1-y0)*t
		p0 := Point{x0, y}
		p1 := Point{x1, y}
		segments := split(circles, p0, p1, f)
		for _, s := range segments {
			clipped := split(outer, s.P0, s.P1, g)
			for _, cs := range clipped {
				fmt.Fprintf(file, "%g,%g %g,%g\n", cs.P0.X, cs.P0.Y, cs.P1.X, cs.P1.Y)
			}
		}
	}

	for _, c := range circles {
		points := c.Discretize(360)
		for i := 1; i < len(points); i++ {
			p0 := points[i-1]
			p1 := points[i]
			clipped := split(outer, p0, p1, g)
			for _, cs := range clipped {
				fmt.Fprintf(file, "%g,%g %g,%g\n", cs.P0.X, cs.P0.Y, cs.P1.X, cs.P1.Y)
			}
		}
	}

	points := outer[0].Discretize(360)
	for _, p := range points {
		fmt.Fprintf(file, "%g,%g ", p.X, p.Y)
	}
	fmt.Fprintf(file, "\n")

	return nil
}

func main() {
	d0 := 1.0
	d1 := math.Pi
	n := 48
	for i := 0; i < n; i++ {
		t := float64(i) / float64(n-1)
		d := d0 + (d1-d0)*t
		path := fmt.Sprintf("overlapping_circles/%.8f.axi", d)
		fmt.Println(path)
		run(path, d, S)
	}
}
