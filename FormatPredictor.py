import FormatAnalyzer
import FormatTokenizer
from utils import is_ascii,is_noise
from utils import fixed_variable_name, divide_consecutive_vars, normalize_index

class FormatPredictResult:
	def __init__(self,analyzed_root=None,var_information=None):
		self.analyzed_root = analyzed_root
		self.var_information = var_information

def format_predictor(format,samples):
	format = format.replace("\n"," ").replace("…"," ").replace("..."," ").replace(".."," ").replace("\ "," ").replace("}","} ").replace("　"," ")
	format = divide_consecutive_vars(format)
	format = normalize_index(format)
	format = format.replace("{","").replace("}","")
	tokens = [x for x in format.split(" ") if x != "" and is_ascii(x) and not is_noise(x)];
	tokenize_result = FormatTokenizer.get_all_format_probabilities(tokens)

	for to_1d_flag in [False,True]:
		for candidate_format in tokenize_result:
			rootnode,varinfo = FormatAnalyzer.format_analyse(candidate_format,to_1d_flag)
			try:
				current_dic = {}
				for sample in samples:
					sample = sample[0].replace("\n"," ")
					tokens = [x for x in sample.split(" ") if x != ""]
					current_dic = rootnode.verifyAndGetTypes(tokens,current_dic)

				for k,var in current_dic.items():
					varinfo[k].type = var[1]
				return FormatPredictResult(rootnode,varinfo)
			except:
				pass

	return None

