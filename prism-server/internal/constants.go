package internal

const (
	MAX_AGE     = 80
	MIN_AGE     = 18
	SALARY_STD  = 87500  // US population standard dev, chatgpt.
	SALARY_MEAN = 100000 // US population mean, chatgpt and other sources.

	// As a percentage of salary
	BUDGET_STD  = .20 // US population standard dev, chatgpt.
	BUDGET_MEAN = .15 // US population mean, chatgpt and other sources.
)

var UNIQUE_INDUSTRIES = [...]string{
	"Trade and Services",
	"Manufacturing",
	"Real Estate and Construction",
	"Finance or Crypto Assets",
	"Finance",
	"Crypto Assets",
	"Industrial Applications and Services",
	"Technology",
	"International Corp Fin",
	"Structured Finance",
	"Energy and Transportation",
	"Life Sciences",
}
