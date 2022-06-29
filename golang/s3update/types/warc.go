package types

type Warc struct {
	Filename string `csv:"warc_filename"`
	Offset   int    `csv:"warc_record_offset"`
	Length   int    `csv:"warc_record_length"`
}
