
import argparse
import os
from functools import reduce
from time import sleep
from time import time

BIBLE_BOOKS = {
	"Genesis": 50,
	"Exodus": 40,
	"Leviticus": 27,
	"Numbers": 36,
	"Deuteronomy": 34,
	"Joshua": 24,
	"Judges": 21,
	"Ruth": 4,
	"1 Samuel": 31,
	"2 Samuel": 24,
	"1 Kings": 22,
	"2 Kings": 25,
	"1 Chronicles": 29,
	"2 Chronicles": 36,
	"Ezra": 10,
	"Nehemiah": 13,
	"Esther": 10,
	"Job": 42,
	"Psalms": 150,
	"Proverbs": 31,
	"Ecclesiastes": 12,
	"Song of Solomon": 8,
	"Isaiah": 66,
	"Jeremiah": 52,
	"Lamentations": 5,
	"Ezekiel": 48,
	"Daniel": 12,
	"Hosea": 14,
	"Joel": 3,
	"Amos": 9,
	"Obadiah": 1,
	"Jonah": 4,
	"Micah": 7,
	"Nahum": 3,
	"Habakkuk": 3,
	"Zephaniah": 3,
	"Haggai": 2,
	"Zechariah": 14,
	"Malachi": 4,
	"Matthew": 28,
	"Mark": 16,
	"Luke": 24,
	"John": 21,
	"Acts": 28,
	"Romans": 16,
	"1 Corinthians": 16,
	"2 Corinthians": 13,
	"Galatians": 6,
	"Ephesians": 6,
	"Philippians": 4,
	"Colossians": 4,
	"1 Thessalonians": 5,
	"2 Thessalonians": 3,
	"1 Timothy": 6,
	"2 Timothy": 4,
	"Titus": 3,
	"Philemon": 1,
	"Hebrews": 13,
	"James": 5,
	"1 Peter": 5,
	"2 Peter": 3,
	"1 John": 5,
	"2 John": 1,
	"3 John": 1,
	"Jude": 1,
	"Revelation": 22,
}
TOTAL_CHAPTER_COUNT:int = reduce(lambda a, b: a+b, list(BIBLE_BOOKS.values()))

BOOK_NAME_FORMAT = "{version}-{order}-{book}"
CHAPTER_NAME_FORMAT = "{version}-{book}-{chapter}"
DIVIDER_DEFAULT = "_"
VERSION_DEFAULT = "kjv"

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

def main():
	parser = argparse.ArgumentParser(
		prog="Obsidian Bible Gateway Markdown Downloader",
		description="Downloads an entire bible from Bible Gateway inf markdown format",
	)
	parser.add_argument(
		"-b",
		"--boldwords",
		action='store_true',
		help="Disables bolding the words of Jesus.",
	)
	parser.add_argument(
		"-c",
		"--copyright",
		action='store_true',
		help="Excludes copyright notice from files.",
	)
	parser.add_argument(
		"-d",
		"--divider",
		default = DIVIDER_DEFAULT,
		help = f"Set a custom replacement for spaces in book file/folder names. For example, you can change the spaces in '1 Samuel' or 'Song of Solomon' Default: '{DIVIDER_DEFAULT}'",
	)
	parser.add_argument(
		"-e",
		"--headers",
		action='store_true',
		help="Exclude editorial headers from output.",
	)
	parser.add_argument(
		"-f",
		"--footnotes",
		action='store_true',
		help="Exclude footnotes from output.",
	)
	parser.add_argument(
		"-r",
		"--crossrefs",
		default='store_true',
		help="Exclude cross-refs from output.",
	)
	parser.add_argument(
		"--chaptername",
		default = CHAPTER_NAME_FORMAT,
		help = f"Specify a custom format for chapter file names. Default: '{CHAPTER_NAME_FORMAT}'. Use '{{Book}}' and '{{Version}}' for capitalized variants.",
	)
	parser.add_argument(
		"--bookname",
		default = BOOK_NAME_FORMAT,
		help = f"Specify a custom format for book folder names. Default: '{BOOK_NAME_FORMAT}'. Use '{{Book}}' and '{{Version}}' for capitalized variants.",
	)
	parser.add_argument(
		"-v",
		"--version",
		help = f"REQUIRED - Specify the bible version to download. Example: '{VERSION_DEFAULT}'",
	)
	
	args = parser.parse_args()

	if not args.version:
		parser.print_help()
		return

	Downloader(args).generate_bible()


class Downloader():
	REQUEST_COOLDOWN:float = 0.1

	book_name_format:str = ""
	chapter_name_format:str = ""
	divider:str = " "
	version:str = ""

	boldwords:str = ""
	copyright:str = ""
	crossrefs:str = ""
	footnotes:str = ""
	headers:str = ""

	_since_last_request = 0
	_downloaded_chapter_count = 0

	def __init__(self, args) -> None:
		self.book_name_format = args.bookname
		self.chapter_name_format = args.chaptername
		self.divider = args.divider
		self.version = args.version.upper()

		self.boldwords = "" if args.boldwords else "-b"
		self.crossrefs = "-r" if args.crossrefs else ""
		self.copyright = "-c" if args.copyright else ""
		self.footnotes = "-f" if args.footnotes else ""
		self.headers = "-e" if args.headers else ""
			

	def get_book_for_file(self, book:str) -> str:
		return book.replace(" ", self.divider)


	def get_chapter_filename(self, book:str, chapter:int) -> str:
		"""
		Returns the name of a chapter's file, minus the file extension.
		"""
		justified_chapter:str = ""
		if BIBLE_BOOKS[book] <= 9:
			justified_chapter = str(chapter).rjust(1, '0')
		elif BIBLE_BOOKS[book] <= 99:
			justified_chapter = str(chapter).rjust(2, '0')
		else:
			justified_chapter = str(chapter).rjust(3, '0')

		return self.chapter_name_format.format(
			Book = self.get_book_for_file(book),
			book = self.get_book_for_file(book).lower(),
			Order = justified_chapter,
			order = justified_chapter,
			Chapter = justified_chapter,
			chapter = justified_chapter,
			Version = self.version,
			version = self.version.lower(),
		)


	def get_chapter_naviagation(self, book:str, chapter:int) -> str:
		prev:str = ""
		back_to_book:str = ""
		post:str = ""

		if chapter != 1:
			prev = f"[[{self.get_chapter_filename(book, chapter-1)}|« {book} {chapter-1}]] | "
		back_to_book = f"[[{self.get_chapter_filename(book, 1)}|{book}]]"
		if chapter != BIBLE_BOOKS[book]:
			post = f" | [[{self.get_chapter_filename(book, chapter+1)}|{book} {chapter+1} »]]"

		return f"### Navigation\n{prev}{back_to_book}{post}"


	def get_bible_path(self) -> str:
		return f"bin/{self.version.lower()}"


	def get_book_path(self, book:str) -> str:
		book_order = list(BIBLE_BOOKS.keys()).index(book)+1
		justified_book_order = str(book_order).rjust(2, '0')
		folder_name = self.book_name_format.format(
			Book = self.get_book_for_file(book),
			book = self.get_book_for_file(book).lower(),
			Order = justified_book_order,
			order = justified_book_order,
			Chapter = justified_book_order,
			chapter = justified_book_order,
			Version = self.version,
			version = self.version.lower(),
		)
		return f"{self.get_bible_path()}/{folder_name}"


	def get_chapter_path(self, book:str, chapter:int) -> str:
		filename = self.get_chapter_filename(book, chapter)
		return f"{self.get_book_path(book)}/{filename}.md"


	def generate_bible(self):
		if not os.path.exists("bin"):
			os.mkdir("bin")

		bible_path = self.get_bible_path()
		if not os.path.exists(bible_path):
			os.mkdir(bible_path)
		
		for book in BIBLE_BOOKS:
			self.generate_book(book)
		
		print("FINISHED!")



	def generate_book(self, book:str):
		book_path = self.get_book_path(book)
		if not os.path.exists(book_path):
			os.mkdir(book_path)
		
		for i in range(BIBLE_BOOKS[book]):
			chapter = i+1
			self.generate_chapter(book, chapter)
			

	def generate_chapter(self, book:str, chapter:int):
		chapter_path = self.get_chapter_path(book, chapter)
		if os.path.exists(chapter_path):
			return

		flags = f"{self.boldwords} {self.copyright} {self.headers} {self.crossrefs} -l -v {self.version}"
		command = f"ruby bg2md.rb {flags} {book.replace(' ', '_')}.{chapter} > \"{chapter_path}\""

		wait_time = max(self._since_last_request - (time()+self.REQUEST_COOLDOWN), 0.0)
		if wait_time != 0.0:
			sleep(wait_time)

		os.system(command)
		self._since_last_request = time()
		self.parse_chapter_file(chapter_path, book, chapter)

		self._downloaded_chapter_count += 1
		
		if book == "Genesis" and chapter == 1:
			pass
		else:
			print(f"{LINE_UP}{LINE_CLEAR}", end="\r")
		print(f"Downloaded {book} {chapter} ({self.version}) - {self._downloaded_chapter_count}/{TOTAL_CHAPTER_COUNT} chapters downloaded.")


	def parse_chapter_file(self, path:str, book:str, chapter:int):
		text = ""
		with open(path, "r+") as file:
			state = 0
			navigation = self.get_chapter_naviagation(book, chapter)
			for line in file.readlines():
				match state:
					case 0:
						text += line
						if line.startswith("# "):
							text += f"""\n{navigation}\n\n"""
							state = 1
					case 1:
						# Looping through verses
						if line.startswith("###### "):
							second_space_index = line.find(" ", 7)
							verse_number = line[0:second_space_index]
							verse_text = line[second_space_index:-1]
							text += f"{verse_number}\n{verse_text}\n"
						else:
							if line.startswith("### Footnotes"):
								text += f"""{navigation}\n\n"""
								state = 2
							text += line
					case 2:
						text += line
			
			file.seek(0)
			file.write(text)
			file.truncate()


if __name__ == "__main__":
    main()