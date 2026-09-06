package com.mc.pgs.lab2.tta;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

/**
 * Structural rules that fail the build rather than a review.
 *
 * <p>Package patterns are anchored to {@code com.mc.pgs.lab2.tta} rather than written as
 * {@code ..api..}: an unanchored pattern also matches third-party packages such as
 * {@code org.assertj.core.api}. Tests are excluded; these rules describe production shape.
 */
@AnalyzeClasses(
        packages = "com.mc.pgs.lab2.tta",
        importOptions = ImportOption.DoNotIncludeTests.class)
class TtaArchitectureIT {

    private static final String API = "com.mc.pgs.lab2.tta.api..";
    private static final String CLIENT = "com.mc.pgs.lab2.tta.client..";
    private static final String CONTRACT = "com.mc.pgs.lab2.tta.client.contract..";
    private static final String MODEL = "com.mc.pgs.lab2.tta.model..";

    @ArchTest
    static final ArchRule controllersDoNotCallDownstreamDirectly =
            noClasses().that().resideInAPackage(API)
                    .should().dependOnClassesThat().resideInAPackage(CLIENT)
                    .because("controllers hold HTTP concerns only; the downstream call belongs to the service layer");

    @ArchTest
    static final ArchRule generatedContractTypesStayOffTheCallerFacingSurface =
            noClasses().that().resideInAnyPackage(API, MODEL)
                    .should().dependOnClassesThat().resideInAPackage(CONTRACT)
                    .because("the generated downstream contract is a boundary artifact; leaking it into this "
                            + "service's own API or model would make a downstream contract change a "
                            + "caller-visible breaking change");

    @ArchTest
    static final ArchRule noSettlementArtifactIsEverProduced =
            noClasses().that().resideInAPackage("com.mc.pgs.lab2.tta..")
                    .should().haveSimpleNameContaining("Settlement")
                    .because("settlement, injection, LCS and DCF are downstream and outside this seam");
}
