from analyzer import ask_ai
from optimizer import generate_action_plan
from prompt_generator import generate_search_prompts
from recommender import generate_recommendations
from scoring import analyze_answer, summarize_results, calculate_share_of_voice
from utils import add_timestamp, create_raw_answer_dataframe


def get_competitors():
    return [
        "Biologique Recherche",
        "ZO Skin Health",
        "Environ",
        "DMK",
        "iS Clinical",
        "PCA Skin",
        "Skinbetter Science",
        "Mesoestetic",
        "Universkin",
        "Cellcosmet"
    ]


def run_visibility_analysis(
    brand,
    category,
    market,
    audience,
    answer_language,
    report_language,
    fixed_prompts,
    on_progress=None,
):
    competitors = get_competitors()

    ai_prompts = generate_search_prompts(
        brand=brand,
        competitors=competitors,
        category=category,
        market=market,
        audience=audience,
        output_language=answer_language
    )

    prompts = fixed_prompts + ai_prompts

    all_results = []
    raw_answers = []
    total_prompts = len(prompts)

    for index, item in enumerate(prompts):
        prompt_category = item["category"]
        prompt = item["prompt"]

        if on_progress is not None:
            on_progress(index, total_prompts, item.get("category", "Unknown"))

        answer = ask_ai(prompt, answer_language)

        raw_answers.append({
            "prompt_category": prompt_category,
            "prompt": prompt,
            "answer": answer
        })

        rows = analyze_answer(
            prompt_category=prompt_category,
            prompt=prompt,
            answer=answer,
            brand=brand,
            competitors=competitors
        )

        all_results.extend(rows)

    detailed_df, summary_df = summarize_results(all_results)
    summary_df = calculate_share_of_voice(summary_df)

    detailed_df = add_timestamp(detailed_df)
    summary_df = add_timestamp(summary_df)

    raw_answer_df = create_raw_answer_dataframe(raw_answers)

    recommendations = generate_recommendations(
        brand=brand,
        category=category,
        market=market,
        audience=audience,
        summary_table=summary_df.to_string(index=False),
        detailed_table=detailed_df.head(40).to_string(index=False),
        report_language=report_language
    )

    plan = generate_action_plan(
        brand=brand,
        detailed_df=detailed_df,
        summary_df=summary_df,
        raw_answers=raw_answers,
        report_language=report_language
    )

    return {
        "competitors": competitors,
        "prompts": prompts,
        "ai_prompts": ai_prompts,
        "detailed_df": detailed_df,
        "summary_df": summary_df,
        "raw_answer_df": raw_answer_df,
        "raw_answers": raw_answers,
        "recommendations": recommendations,
        "plan": plan,
    }
