package resolve

import (
	"testing"
)

func TestIO(t *testing.T) {
	tests := []struct {
		r    *R
		in   []string
		want string
	}{
		{&R{}, []string{}, ""}, // 0
		{ // 1
			&R{NoExt: true},
			[]string{"/bob/hello.abc", "there.123.456"},
			"/bob/hello\nthere.123",
		}, { // 2
			&R{ToBaseName: true},
			[]string{"/bob/hello.abc", "there.123.456"},
			"hello.abc\nthere.123.456",
		}, { // 3
			&R{ToBaseName: true, NoExt: true},
			[]string{"/bob/hello.abc", "there.123.456"},
			"hello\nthere.123",
		}, { // 4
			&R{G3: true},
			[]string{"//depot/google3/one/two/three/bob/hello.c#12"},
			"one/two/three/bob/hello.c",
		}, { // 5
			&R{G3: true},
			[]string{"blaze-bin/one/two/three/bob/hello.go"},
			"one/two/three/bob/hello.go",
		}, { // 6
			&R{UpDirCount: -1},
			[]string{"f.ext", "a/f.ext", "a/b/f.ext", "/a/b/f.ext"},
			"f.ext\nf.ext\na/f.ext\n/a/f.ext",
		}, { // 7
			&R{ToDir: true},
			[]string{"a/b/c.ext", "a/b/e.ext"},
			"a/b\na/b",
		}, { // 8
			&R{ToDir: true, Unique: true},
			[]string{"a/b/c.ext", "a/b/e.ext"},
			"a/b",
		},
	}
	for i, test := range tests {
		for _, line := range test.in {
			test.r.Resolve(line)
		}
		got := test.r.String()
		if got != test.want {
			t.Errorf("%d: String(%v) = %q, want %q", i, test.in, got, test.want)
		}
	}
}
