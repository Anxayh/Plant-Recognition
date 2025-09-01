import streamlit as st
from PIL import Image
import google.generativeai as genai
import os

# --- 页面基础配置 ---
st.set_page_config(
    page_title="植物识别相机",
    page_icon="🌿",
    layout="centered"
)

try:
    # 从 Streamlit secrets 获取 API Key
    api_key = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError):
    # 如果 secrets 中没有，尝试从环境变量获取
    api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("错误： API Key 未配置。请在 Streamlit secrets 或环境变量中设置 GOOGLE_API_KEY。")
    st.stop()

genai.configure(api_key=api_key)


# --- 功能函数 ---
def get_plant_info(image_data):
    """
    调用 Gemini 模型识别图片中的植物并获取百科信息。
    """
    try:
        # 初始化模型
        model = genai.GenerativeModel('gemini-2.5-flash')

        # 准备模型输入
        image_part = {
            "mime_type": "image/jpeg",
            "data": image_data
        }
        prompt = """
        请识别这张图片中的主要植物是什么？请只提供以下信息：
        1.  **植物名称**：最可能的物种名称（中文和学名）。
        2.  **百科资料**：一段简洁的、适合普通人阅读的百科介绍，包括其主要特征、生长习性、分布范围和常见用途等。
        3.  **附加信息**：如果是花卉，请附上简短的对于该种类花卉养护注意事项；如果是蔬菜，请附上两个使用该蔬菜的简单菜谱；若为蔬菜花卉以外的植物，则不显示附加信息。
        请使用 Markdown 格式化你的回答，突出标题。如果图片中没有植物或无法识别，请友好地告知用户。
        """


        # 调用模型
        response = model.generate_content([prompt, image_part])

        # 返回模型的文本响应
        return response.text
    except Exception as e:
        # 处理 API 调用可能出现的异常
        return f"识别过程中发生错误：{e}"


# --- 页面 UI ---
st.title("🌿 植物识别相机")
st.markdown("---")
st.write("你好！上传一张植物照片，我将尽力识别它的品种和信息。")

# 图片上传组件
uploaded_file = st.file_uploader(
    "请选择一张本地图片...",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # 显示上传的图片
    st.image(uploaded_file, caption="你上传的图片", use_column_width=True)

    # 显示一个加载状态提示
    with st.spinner('正在努力识别中，请稍候...'):
        try:
            # 打开图片
            image = Image.open(uploaded_file)

            # 将图片转换为字节流，以便发送给 API
            # 注意：Gemini API 要求图片数据是原始字节
            img_byte_arr = uploaded_file.getvalue()

            # 调用识别函数
            plant_info = get_plant_info(img_byte_arr)

            # 显示识别结果
            st.markdown("---")
            st.subheader("🔍 识别结果")
            st.markdown(plant_info)

        except Exception as e:
            st.error(f"处理图片时发生错误：{e}")

else:
    st.info("请先上传一张图片，开始你的植物发现之旅吧！")

# --- 页脚 ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: grey;'>"
    "V1.1"
    "</div>",
    unsafe_allow_html=True
)