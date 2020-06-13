package main

import (
	"errors"
	"flag"
	"fmt"
	"math"
	"strconv"
	"time"
)

func ParseTimestamp(unixTime int64) (out string, err error) {
	unixNano := time.Now().UnixNano()
	secs := math.Abs(float64(unixNano - unixTime * int64(time.Second)))
	msecs := math.Abs(float64(unixNano - unixTime * int64(time.Millisecond)))
	nsecs := math.Abs(float64(unixNano - unixTime))
	minValue := math.Min(math.Min(secs, msecs), nsecs)
	var t time.Time
	if minValue == secs {
		t = time.Unix(unixTime, 0)
	} else if minValue == msecs {
		t = time.Unix(unixTime / int64(time.Millisecond), unixTime % int64(time.Millisecond))
	} else {
		t = time.Unix(unixTime / int64(time.Microsecond), unixTime % int64(time.Microsecond))
	}
	out = t.UTC().Format(time.RFC3339)
	return out, nil
}

func ParseDateTime(in string) (out string, err error) {
	var t time.Time
	t, err = time.Parse(time.RFC3339, in)
	if err == nil {
		out = strconv.FormatInt(t.UnixNano() / 1000, 10)
		return out, nil
	}
	var d time.Duration
	d, err = time.ParseDuration(in)
	if err == nil {
		t = time.Now().Add(-d)
		out = strconv.FormatInt(t.UnixNano() / 1000, 10)
		return out, nil
	}
	err = errors.New(fmt.Sprintf("Unable to parse %s as a date", in))
	return "", err
}

func ParseTime(in string) (out string, err error) {
	unixTime, err := strconv.ParseInt(in, 0, 64)
	if err == nil {
		return ParseTimestamp(unixTime)
	} else {
		return ParseDateTime(in)
	}
}

func main() {
	flag.Parse()
	for _, timeString := range flag.Args() {
		out, err := ParseTime(timeString);
		if err != nil {
			fmt.Println(err);
		}
		fmt.Printf("%s\n", out);
	}
}

