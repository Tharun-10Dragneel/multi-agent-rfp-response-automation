import { NextResponse } from "next/server";
import { db } from "@/src/db/index";
import { rfpsTable } from "@/src/db/schema";
import { createServerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";

export async function POST(req: Request) {
  try {
    const body = await req.json();

    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!,
      { cookies }
    );

    const {
      data: { user },
    } = await supabase.auth.getUser();

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const [rfp] = await db
      .insert(rfpsTable)
      .values({
        title: body.title,
        clientName: body.client,
        description: body.description,
        submissionDate: body.submissionDate,
        submittedBy: user.id, // 👈 authoritative
      })
      .returning();

    return NextResponse.json({ rfp });
  } catch (err) {
    console.error(err);
    return NextResponse.json(
      { error: "Failed to create RFP" },
      { status: 500 }
    );
  }
}
