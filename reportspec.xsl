<xsl:transform
    version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:h="http://www.w3.org/1999/xhtml">

<xsl:template match="h:html">
  <xsl:variable name="fs"
		select="substring-after('font-size: ', h:body/@style)"/>
  <xsl:variable name="o">
    <xsl:choose>
      <xsl:when test="contains(h:body/@class, 'landscape')"
		>landscape</xsl:when>
      <xsl:otherwise>portrait</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <Report fontSize="{$fs}" orientation="{$p}">
    <xsl:apply-templates />
  </Report>
</xsl:template>


<xsl:template match="h:h1">
  <xsl:variable name="fs" select="substring-after('font-size: ', @style)"/>
  <ReportHeader>
    <Output>
      <!-- todo: trigger black/white on class="reversed" -->
      <Line fontSize="$fs" bgcolor="'black'" color="'white'">
	<literal width="2"/>
	<literal width="30" align="left">
	  <xsl:value-of select="text()" />
	</literal>
      </Line>
    </Output>
  </ReportHeader>
</xsl:template>

<xsl:template match="h:h2">
  <PageHeader>
    <Output>
      <HorizontalLine size="4" bgcolor="'white'"/>
      <Line fontSize="11" bgcolor="'0xd0d0d0'" color="'black'">
	<literal width="2"/>
	<literal width="40" align="left">
	  <xsl:value-of select="text()"/>
	</literal>
	<literal width="10"/>
	<field value="stod(m.report_date)" fontSize="8"/>
	<literal width="10"/>
	<literal fontSize="8">pg. </literal>
	<field value="r.pageno" fontSize="8"/>
      </Line>
      <HorizontalLine size="2" bgcolor="'white'" />
    </Output>
  </PageHeader>
</xsl:template>

<xsl:template match="h:thead">
  <Detail>

    <FieldHeaders>
      <Output>
	<HorizontalLine size="1" bgcolor="'black'"/>
	<Line bgcolor="'0xe5e5e5'" bold="true">
	  <literal width="1"/>
	  <literal width="10" align="center">Earliest</literal>
	  <literal width="1"/>
	  <literal width="10" align="center">Latest</literal>
	  <literal width="1"/>
	  <literal width="30" align="center">Client</literal>
	  <literal width="1"/>
	  <literal width="9" align="right">Charges</literal>
	  <literal width="1"/>
	  <literal width="9" align="right">Client pd</literal>
	  <literal width="1"/>
	  <literal width="9" align="right">Ins. Pd</literal>
	  <literal width="1"/>
	  <literal width="9" align="right">Due</literal>
	</Line>
	<HorizontalLine size="1" bgcolor="'black'"/>
	<HorizontalLine size="4" bgcolor="'white'"/>
      </Output>
    </FieldHeaders>		

    <FieldDetails>
      <Output>
	<Line bgcolor="iif(r.detailcnt%2,'0xe5e5e5','white')">
	  <literal width="1"/>
	  <field width="10" align="right" value="stod(earliest)"/>
	  <literal width="1"/>
	  <field width="10" align="right" value="stod(latest)"/>
	  <literal width="1"/>
	  <field width="30" align="left" value="client_name"/>
	  <literal width="1"/>
<!--
-->
	  <field width="9" align="right" value="charges"/>
	  <literal width="1"/>
	  <field width="9" align="right" value="client_paid"/>
	  <literal width="1"/>
	  <field width="9" align="right" value="insurance_paid"/>
	  <literal width="1"/>
	  <field width="9" align="right" value="due"/>
	</Line>
      </Output>
    </FieldDetails>
  </Detail>


</xsl:transform>
